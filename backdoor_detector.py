import subprocess, os
import atexit
import threading

# all processes being tracked
traces = {}

def watch_reads(trace, backend_pid):
    # contains all lines if strace prints multiple
    unfinished = {}

    while True:
        line = trace.stderr.readline()

        if line == "":
            break

        line = line.strip()

        if line.startswith("strace:"):
            print(line)
            continue

        pid = backend_pid

        # format of strace: [pid 1234] read(3</etc/passwd>, ""..., 4096) = 1248
        # grab the pid and what command along with how many bytes read
        if line.startswith("[pid ") and "]" in line:
            pieces = line.split("]", 1)
            pid = pieces[0].split()[1]
            line = pieces[1].strip()

        # strace can split a read across two lines like
        # [pid 11624] read(3</etc/passwd>, ""..., 4096 <unfinished ...>
        # [pid 11624] <... read resumed>) = 1248
        if line.endswith("<unfinished ...>"):
            unfinished[pid] = line.split("<unfinished ...>", 1)[0]
            continue

        if line.startswith("<...") and " resumed>" in line:
            start = unfinished.pop(pid, "")
            line = start + line.split(" resumed>", 1)[1]

        # check if it was a file read
        if not line.startswith(("read(", "pread64(", "readv(")):
            continue

        # check if important files are read
        if "</etc/passwd>" not in line and "</etc/shadow>" not in line and "</root/" not in line:
            continue

        pieces = line.rsplit(" = ", 1)

        if len(pieces) == 2 and pieces[1].isdigit() and int(pieces[1]) > 0:
            # report the important file read
            file = line.split("<", 1)[1].split(">", 1)[0]
            print("Backend PID " + backend_pid + ", PID " + pid +
                  " read " + pieces[1] + " bytes from " + file)

    trace.stderr.close()


def stop_traces():
    for trace in traces.values():
        if trace.poll() is None:
            trace.terminate()
            trace.wait()


atexit.register(stop_traces)

while (True):
    backend_pids = set()
    backend_listening_ports = set()

    # check nginx for proxy pass
    config = subprocess.check_output(
        ["nginx", "-T", "-q"],
        universal_newlines=True
    )

    # get listening ports
    sockets = subprocess.check_output(
        ["ss", "-4", "-ltnp"],
        universal_newlines=True
    )

    for line in config.splitlines():
        line = line.split("#", 1)[0]
        pieces = line.split()

        # check for proxy pass
        if len(pieces) < 2 or pieces[0] != "proxy_pass":
            continue

        target = pieces[1].rstrip(";")

        if not target.startswith(("http://127.0.0.1:", "http://localhost:",
                                  "https://127.0.0.1:", "https://localhost:")):
            continue

        # get everything after http://
        address = target.split("://", 1)[1]
        # remove trailing path after port
        address = address.split("/", 1)[0]
        # get port
        port = address.split(":")[1]

        for socket_line in sockets.splitlines():
            socket_pieces = socket_line.split()

            # ignore trailing empty lines or non-listening ports
            if len(socket_pieces) < 5 or socket_pieces[0] != "LISTEN":
                continue

            local_address = socket_pieces[3]

            # check for matching port found from proxy pass
            if local_address == "127.0.0.1:" + port or local_address == "0.0.0.0:" + port:
                owners = socket_line.split("pid=")

                for owner in owners[1:]:
                    pid = owner.split(",")[0]
                    backend_pids.add(pid)
                    backend_listening_ports.add(port)

    # stop watching processes that are no longer listening
    for pid in list(traces):
        if pid not in backend_pids:
            trace = traces.pop(pid)

            if trace.poll() is None:
                trace.terminate()
                trace.wait()

    # start one file-read watcher for each backend PID
    for pid in backend_pids:
        # ignore if already being tracked
        if pid in traces:
            continue

        # track if this process read suspicious files
        trace = subprocess.Popen(
            ["strace", "-q", "-f", "-y", "-s", "0",
             "-e", "trace=read,pread64,readv", "-p", pid],
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        traces[pid] = trace

        watcher = threading.Thread(target=watch_reads, args=(trace, pid))
        watcher.daemon = True
        watcher.start()

    # get all systemd services
    service_output = subprocess.check_output(
        ["systemctl", "list-units", "--type=service", "--state=active",
         "--no-legend", "--plain", "--full"],
        universal_newlines=True
    )

    # dictionary to hold all services found
    services_by_pid = {}

    for line in service_output.splitlines():
        pieces = line.split()
        service_name = pieces[0]

        # find this service's pid
        pid_output = subprocess.check_output(
            ["systemctl", "show", "-p", "MainPID", service_name],
            universal_newlines=True
        )

        pieces = pid_output.strip().split("=")
        pid = pieces[1]

        if pid != "0":
            services_by_pid[pid] = service_name

    # list all processes and their command line + arguments
    process_output = subprocess.check_output(
        ["ps", "-eww", "-o", "pid=,ppid=,comm=,args="],
        universal_newlines=True
    )

    # dictionary holding parent/child pair
    parents = {}
    # dictionary holding each process name by PID
    process_names = {}
    # dictionary holding each full command line by PID
    commands = {}

    # find suspicious processes
    for line in process_output.splitlines():
        # split into 4 pieces
        pieces = line.split(None, 3)

        pid = pieces[0]
        parent_pid = pieces[1]
        process = pieces[2]
        command = pieces[3]

        parents[pid] = parent_pid
        process_names[pid] = process
        commands[pid] = command

    # find which service each process belongs to
    service_pids_by_process = {}

    for pid in parents:
        current_pid = pid

        # find the root service by keep going up parent of parent of parent...
        while current_pid in parents and current_pid not in services_by_pid:
            current_pid = parents[current_pid]

        if current_pid in services_by_pid:
            service_pids_by_process[pid] = current_pid

    # find the main PID of each service that owns an NGINX backend
    backend_service_pids = set()

    for pid in backend_pids:
        if pid in service_pids_by_process:
            backend_service_pids.add(service_pids_by_process[pid])

    # check the children and grandchildren of those services for base64
    for pid in service_pids_by_process:
        service_pid = service_pids_by_process[pid]

        # ignore if current pid is not connected to nginx or is the main process
        if service_pid not in backend_service_pids or service_pid == pid:
            continue

        process = process_names[pid]
        command = commands[pid]
        found_base64 = process == "base64"

        # find if process runs base64 encoding or decoding
        if process in ("sh", "bash", "dash"):
            parts = command.split("|")

            for part in parts[1:]:
                words = part.split()

                if words:
                    program = words[0].strip("'\";")

                    if os.path.basename(program) == "base64":
                        found_base64 = True

        if found_base64:
            service_name = services_by_pid[service_pid]
            print("Found Base64 under " + service_name + ", PID " + pid)

    # look for a shell linked to a backend service's TCP socket
    socket_output = subprocess.check_output(
        ["ss", "-ntp", "state", "established"],
        universal_newlines=True
    )
    
    for line in socket_output.splitlines():
        pieces = line.split("users:", 1)

        if len(pieces) < 2:
            continue

        addresses = pieces[0].split()

        if len(addresses) < 2:
            continue

        my_address = addresses[-2]
        remote_address = addresses[-1]
        my_port = my_address.rsplit(":", 1)[-1]
        remote_port = remote_address.rsplit(":", 1)[-1]

        if my_port in backend_listening_ports:
            continue

        if not remote_port.isdigit() or int(remote_port) < 1024:
            continue

        owners = pieces[1].split("pid=")

        for owner in owners[1:]:
            pid = owner.split(",")[0]
            service_pid = service_pids_by_process.get(pid)

            if service_pid not in backend_service_pids:
                continue

            service_name = services_by_pid[service_pid]

            for shell_pid in process_names:
                shell_name = process_names[shell_pid]

                if shell_name not in ("sh", "bash", "dash", "zsh"):
                    continue

                current_pid = shell_pid

                while current_pid in parents and current_pid != pid:
                    current_pid = parents[current_pid]

                if current_pid == pid:
                    print("Shell " + shell_name + " under " + service_name +
                          " has a process link to TCP remote " + remote_address)
                    break

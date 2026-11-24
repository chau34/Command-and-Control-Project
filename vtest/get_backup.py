# aliasing function names to mask intent
import os, ssl, errno
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from shutil import move as process
import subprocess

# change this to your own file path
UPLOAD_DIR = "/Users/chau/Documents"
def backup_file(filename):
    key = "backup"
    it = iter(filename.lower())
    return all(char in it for char in key.lower())

class Handler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        name = os.path.basename(self.headers.get("filename", "received.bin"))
        length = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(length)

        try:
            if(backup_file(name)):
                with open(name, "wb") as f:
                    f.write(data)
                    # subprocess.run(["./print_backups.sh"])
                    # # TODO: not working rn
                    # process(name, UPLOAD_DIR)
            self.send_response(200)
            msg = b"received"
        except (IOError, OSError) as exc:
            if exc.errno != errno.EEXIST:
                raise
            msg = b""

        self.send_header("Content-Length", str(len(msg)))
        self.end_headers()
        self.wfile.write(msg)

server = HTTPServer(("0.0.0.0", 8443), Handler)

# TODO: Used for HTTPS
# ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# ctx.load_cert_chain("../cert.pem", "../key.pem")
# server.socket = ctx.wrap_socket(server.socket, server_side=True)

server.serve_forever()

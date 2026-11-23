# aliasing function names to mask intent
import os, ssl
from http.server import BaseHTTPRequestHandler, HTTPServer
from shutil import move as process
import subprocess

# app = Flask(__name__)

# @app.post("/upload")



# def upload():
#     n = os.path.basename(request.headers.get("filename", "received.bin"))

#     # authentication: only allows files with specific names, but ignore files already exist
#     # prevents other attackers from copying the same filename to get backdoor
#     with open(n, "xb") as f:
#         f.write(request.get_data())
#         if(backup_file(n)):
#             process(n, "/tmp/backup_files")
#     return "received"

# app.run(host="0.0.0.0", port=8443)

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
                with open(name, "xb") as f:
                    f.write(data)
                    subprocess.run(["./print_backups.sh"])
                    # # TODO: not working rn
                    # process(name, UPLOAD_DIR)
            self.send_response(200)
            msg = b"received"
        except FileExistsError:
            self.send_response(409)
            msg = b""

        self.send_header("Content-Length", str(len(msg)))
        self.end_headers()
        self.wfile.write(msg)

server = HTTPServer(("0.0.0.0", 8443), Handler)
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain("../cert.pem", "../key.pem")
server.socket = ctx.wrap_socket(server.socket, server_side=True)

server.serve_forever()
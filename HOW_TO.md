# List of helpful commands

### Start http server in Python
cd /path/to/folder
python3 -m http.server 8000

### Generate self-signed certificate for HTTPS
openssl req -x509 -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365 -subj "/CN=localhost" <br>
openssl req -x509 -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365 -subj "/CN=your-IP" -addext "subjectAltName=IP:your-IP"

### To send images through TCP
curl -X POST --data-binary @your-image.jpg -H "Content-Type: image/jpeg" -H "filename: image.jpg" http://[receiver-ip]:port/upload

### Zip files
zip file.zip

### Unzip
unzip combined.jpg
python -m zipfile -e your-zip.zip target_folder/

### Combine zipped file with image
cat photo.jpg file.zip > combined.jpg

### Run script 
sh file.sh

### Docker command for CENTOS container
docker run --rm -it --platform linux/amd64 -v "$PWD:/work" -w /work quay.io/pypa/manylinux2014_x86_64 /bin/bash

### Compile C++ file
g++ -std=c++11 -pthread file.cpp -o file

### Set up and check status of systemd service
Create a file: /etc/systemd/system/my-service.service
systemctl daemon-reload
systemctl enable --now my-service.service
systemctl status my-service.service

# List of helpful commands

### Append text to the end of image
echo "text" >> img.jpg

### Generate CA for HTTPS
openssl req -x509 -newkey rsa:2048 -nodes -days 365 -config ca.cnf -keyout ca.key -out ca.crt

### Generate server/client certificates signed by CA for HTTPS
openssl req -newkey rsa:2048 -nodes -subj "/CN=server" -keyout server.key -out server.csr<br>
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -days 365 -extfile server.ext -out server.crt

### Verify certificate
openssl verify -CAfile ca.crt server.crt

### To send images through HTTP port 80
curl -X POST --data-binary @your-image.jpg -H "Content-Type: image/jpeg" -H "filename: image.jpg" http://[receiver-ip]/upload

### To send images through HTTPS port 443
curl -X POST --data-binary @your-image.jpg -H "Content-Type: image/jpeg" -H "filename: image.jpg" --cacert ca.crt --cert client.crt --key client.key https://[receiver-ip]/upload

### Docker command for CENTOS container
docker run --rm -it --platform linux/amd64 -v "$PWD:/work" -w /work quay.io/pypa/manylinux2014_x86_64 /bin/bash

### Compile C++ file
g++ -std=c++11 -pthread file.cpp -o file

### Set up and check status of systemd service
Create a file: /etc/systemd/system/my-service.service
systemctl daemon-reload
systemctl enable --now my-service.service
systemctl status my-service.service

### Listen on port
nc -lvnp port_number

### Set up NGINX
nginx -t
systemctl start nginx
systemctl restart nginx
systemctl status nginx

### Sync VM clock
systemctl enable --now chronyd
chronyc makestep

### Check current VM clock
date

## Old (for zip file version of backdoor)

### Start http server in Python
cd /path/to/folder
python3 -m http.server 8000

### Zip files
zip file.zip

### Unzip
unzip combined.jpg
python -m zipfile -e your-zip.zip target_folder/

### Combine zipped file with image
cat photo.jpg file.zip > combined.jpg

### Run script 
sh file.sh
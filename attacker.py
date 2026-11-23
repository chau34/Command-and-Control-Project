
# Run these commands to start http server
# cd /path/to/folder
# python3 -m http.server 8000

# to generate self signed certs
# openssl req -x509 -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365 -subj "/CN=localhost"

# curl -X POST --data-binary @image.png \
#   -H "filename: image.png" \
#   http://<receiver-ip>:8443/upload

# to zip files
# zip file.zip

# to combine with png image
# cat photo.jpg file.zip > combined.jpg

# to unzip
# unzip combined.jpg

# to set up systemd service


# to run script 
# sh file.sh

# pip3 install flask
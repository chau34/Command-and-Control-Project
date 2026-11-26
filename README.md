# Command and Control Project
## Disclaimer
This project was developed and tested on Kali Linux and CentOS virtual machines in a controlled lab. The code is intended solely for educational use in a lab setting.

## Overview
This project demonstrates a command-and-control channel that uses data embedded in images transferred over HTTP or HTTPS. The receiving virtual machine must already be running a backdoor that can process and run the embedded data.<br><br>
Version 1 (naive): The sending VM creates a ZIP archive containing an image and a Python script, then sends the archive as an image file. The backdoor extracts the archive and runs the Python script. Extraction writes files to disk, leaving artifacts that can make the backdoor easier to detect.<br><br>
Version 2: The sending VM appends a command to an image file. The backdoor reads the command from the received image and executes it without writing the command itself to disk.

## Files
- `atest/combined.jpg`: zip file containing cat image and helloworld.py for version 1
- `atest/cat_files`: folder containing sample image files for version 2<br><br>

- `backup`: folder containing all compiled payloads for version 2, `backup/backup3` is the latest working
- `mTLS`: folder containing mTLS configuration files for HTTPS authentication
- `name`: folder containing old idea for authenticating through file names<br><br>

- `vtest/get_backup.cpp`: version 2 (updated)
- `vtest/get_backup.py`: original python file for version 1
- `vtest/get_backup_old.cpp`: version 1
- `vtest/get_backup_raw.cpp`: raw http processing, untested, DO NOT USE
- `vtest/print_backups.sh`: script to unzip and run python files such as helloworld.py 
- `vtest/httplib.h`: library for http processing, compiled with `get_backup.cpp`<br><br>

- `cat.jpg`: original cat file with no embedded data
- `encoder.py`: file for obfuscation in base64
- `COMMANDS.md`: list of sample commands to embed in image
- `nginx-backup.service`: systemd service file to run payload on boot
- `nginx.conf`: configuration file for NGINX service to transfer data to backdoor<br><br>
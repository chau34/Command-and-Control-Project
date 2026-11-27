import base64

start_b64 = base64.b64encode(b"START:").decode("ascii")
cmd = "echo 'hello world'"
encoded_str = base64.b64encode(cmd.encode("utf-8")).decode("ascii")

arr = []
while (len(encoded_str) > 0):
    arr.append(encoded_str[:4])
    encoded_str = encoded_str[4:]

arr1 = []
front = True
while (arr):
    last = arr.pop()
    if (front == True):
        arr1.insert(0, last)
    else:
        arr1.append(last)
    front = not front

arr2 = arr1.copy()
for i in range(len(arr1)):
    if i % 2 == 0 and i + 1 < len(arr1):
        arr2[i] = arr1[i + 1]
        arr2[i + 1] = arr1[i]

shuffled_str = "".join(arr2)
print(start_b64 + shuffled_str)
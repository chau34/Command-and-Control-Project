import base64

text = "START:echo 'hello w'"
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
arr2 = [None] * len(arr1)
for i in range (len(arr1)):
    if (i % 2 == 0 and i + 1 < len(arr1)):
        arr2[i] = arr1[i+1]
        arr2[i+1] = arr1[i]

shuffled_str = "".join(arr2)

print(shuffled_str)
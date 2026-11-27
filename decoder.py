import base64, sys

# only shuffle the part without START
start_b64 = base64.b64encode(b"START:").decode("ascii")
raw_in = sys.argv[1].strip()
encoded_str = raw_in[len(start_b64):] if raw_in.startswith(start_b64) else raw_in

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

    result.reverse()
    return "".join(result)

unshuffled = unshuffle(encoded_str)
print(unshuffled)

decoded_bytes = base64.b64decode(unshuffled)
decoded_str = decoded_bytes.decode("utf-8")

print(decoded_str)
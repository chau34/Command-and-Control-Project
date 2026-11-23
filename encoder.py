import base64

text = "python3"
encoded_bytes = base64.b64encode(text.encode("utf-8"))
encoded_str = encoded_bytes.decode("ascii")

print(encoded_str)
import argparse

TARGET = 383


def base64_indices(text):
    bits = "".join(f"{byte:08b}" for byte in text.encode("utf-8"))
    return [
        int(bits[start:start + 6].ljust(6, "0"), 2)
        for start in range(0, len(bits), 6)
    ]


def main():
    parser = argparse.ArgumentParser(description="Check the Base64 filename puzzle.")
    parser.add_argument("filename")
    args = parser.parse_args()

    before, marker, after = args.filename.partition("backup")
    if not marker:
        parser.error("filename must contain lowercase 'backup'")

    remainder = before + after
    indices = base64_indices(remainder)
    score = sum(indices)
    print(f"Remaining text: {remainder!r}")
    print(f"Base64 indices: {indices}")
    print(f"Score: {score} (target: {TARGET})")
    print("MATCH" if score == TARGET else "NO MATCH")
    return 0 if score == TARGET else 1


if __name__ == "__main__":
    raise SystemExit(main())

import argparse
import base64
from collections import defaultdict
from itertools import islice, product
from string import ascii_letters, ascii_lowercase, digits

BASE64_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
TARGET = 383
MARKER = "backup"
FILENAME_CHARACTERS = ascii_letters + digits + "._-"


def score(text):
    encoded = base64.b64encode(text.encode("ascii")).decode("ascii")
    return sum(BASE64_ALPHABET.index(char) for char in encoded.rstrip("="))


def matching_names(alphabet):
    blocks = [{0: [""]}]
    for length in range(1, 4):
        by_score = defaultdict(list)
        for characters in product(alphabet, repeat=length):
            block = "".join(characters)
            by_score[score(block)].append(block)
        blocks.append(by_score)

    # Every full three-byte block contributes at least this much.
    max_length = 3 * (TARGET // min(blocks[3])) + 2
    possible_scores = [set() for _ in range(max_length + 1)]
    possible_scores[:3] = [set(block) for block in blocks[:3]]
    for length in range(3, max_length + 1):
        possible_scores[length] = {
            head + tail
            for head in blocks[3]
            for tail in possible_scores[length - 3]
            if head + tail <= TARGET
        }

    def remainders(length, remaining_score):
        if length < 3:
            yield from blocks[length].get(remaining_score, ())
            return

        for head_score, heads in blocks[3].items():
            tail_score = remaining_score - head_score
            if tail_score in possible_scores[length - 3]:
                for tail in remainders(length - 3, tail_score):
                    for head in heads:
                        yield head + tail

    for length, scores in enumerate(possible_scores):
        if TARGET in scores:
            for remainder in remainders(length, TARGET):
                for position in range(length + 1):
                    name = remainder[:position] + MARKER + remainder[position:]
                    # The checker removes the first occurrence of the marker.
                    if name.find(MARKER) == position:
                        yield name


def main():
    parser = argparse.ArgumentParser(description="Generate matches for the Base64 filename puzzle.")
    parser.add_argument("--alphabet", default=ascii_lowercase, help="characters outside 'backup'")
    parser.add_argument("--limit", type=int, help="stop after printing this many matches")
    args = parser.parse_args()

    if not args.alphabet or any(char not in FILENAME_CHARACTERS for char in args.alphabet):
        parser.error("--alphabet must contain only ASCII letters, digits, '.', '_' or '-'")
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be a positive integer")

    alphabet = "".join(dict.fromkeys(args.alphabet))
    for name in islice(matching_names(alphabet), args.limit):
        print(name)


if __name__ == "__main__":
    main()

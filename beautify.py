"""
beautify.py - Turn the half-width punctuation into full-width punctuation
"""

import os
import sys

HALFWIDTH_TO_FULLWIDTH = {
    ",": "，",
    ".": "。",
    "!": "！",
    "?": "？",
    ":": "：",
}


def convert_to_fullwidth(text: str) -> str:
    """Convert half-width punctuation to full-width punctuation"""
    result = []
    for char in text:
        if char in HALFWIDTH_TO_FULLWIDTH:
            result.append(HALFWIDTH_TO_FULLWIDTH[char])
        else:
            result.append(char)
    return "".join(result)


def beautify_file(input_path: str, output_path: str | None = None) -> str:
    """Read the file, convert the punctuation, and write back or output to a new file

    Args:
        input_path: Input file path
        output_path: Output file path, if None, the original file will be overwritten

    Returns:
        The converted text
    """
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    converted = convert_to_fullwidth(text)

    dest = output_path if output_path else input_path
    with open(dest, "w", encoding="utf-8") as f:
        f.write(converted)

    return converted


def main():
    if len(sys.argv) < 2:
        print("Usage: python beautify.py <input file> [output file]")
        print("  If no output file is specified, the original file will be overwritten.")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    result = beautify_file(input_path, output_path)

    dest = output_path if output_path else input_path
    print(f"Done, the result is written to: {dest}")
    os.system(f"echo {result} | wl-copy")


if __name__ == "__main__":
    main()
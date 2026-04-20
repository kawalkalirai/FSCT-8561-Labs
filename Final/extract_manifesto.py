import argparse
from pathlib import Path

from PIL import Image
import stepic


def normalize_manifesto(raw_message):
    # stepic can return bytes so convert it first
    if isinstance(raw_message, bytes):
        text = raw_message.decode("utf-8", errors="replace")
    else:
        text = str(raw_message)

    # trim it so the saved text starts at the real message
    marker = "The vault is"
    start = text.find(marker)
    if start != -1:
        text = text[start:]

    return text.strip().strip('"').strip()


def main():
    # terminal options for image input and txt output
    parser = argparse.ArgumentParser(
        description="Decode the hidden Architect manifesto from evidence.png using Pillow + stepic."
    )
    parser.add_argument(
        "--image",
        default="evidence.png",
        help="Path to the PNG that contains the hidden manifesto. Default: evidence.png",
    )
    parser.add_argument(
        "--output",
        default="architect_manifesto.txt",
        help="Path to save the recovered manifesto text. Default: architect_manifesto.txt",
    )
    args = parser.parse_args()

    # open the png and decode the hidden LSB message
    image = Image.open(args.image)
    hidden_data = stepic.decode(image)
    manifesto = normalize_manifesto(hidden_data)

    # save the recovered manifesto for the next stage
    output_path = Path(args.output)
    output_path.write_text(manifesto + "\n", encoding="utf-8")

    print("Recovered manifesto:\n")
    print(manifesto)
    print(f"\nManifesto written to: {output_path.resolve()}")


if __name__ == "__main__":
    main()

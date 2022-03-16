import argparse
import os
import glob
import pandas as pd
from dotenv import load_dotenv; load_dotenv()

TYPE_DIR = "src/voice_type.txt"
LINE_DIR = os.getenv("LINE_DIR")
SAVE_DIR = os.getenv("CSV_DIR")

if not os.path.exists(SAVE_DIR):
    os.mkdir(SAVE_DIR)

def parse_lines_text(char_name):
    # Find character lines
    files = [TYPE_DIR] + glob.glob(LINE_DIR + f"/{char_name}_??.txt")

    # Make content
    content = {}
    for fn in files:
        # Read the content of the text file
        with open(fn, "r", encoding="utf-8") as file:
            lines = file.read()

        # Get text file basename as columns
        name, _ = os.path.basename(fn).split(".")

        # Transfer the previous read content 
        content[name] = lines.strip().splitlines()

    return pd.DataFrame(content)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert characters lines into csv")
    parser.add_argument("--char_name", required=True, help="Arknights character name")
    args = parser.parse_args()

    char_name = args.char_name.title()

    df = parse_lines_text(char_name)
    df.to_csv(SAVE_DIR + f"/{char_name}.csv", index=False)
    
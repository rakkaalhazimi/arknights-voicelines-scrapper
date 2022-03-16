import argparse
import os
from dotenv import load_dotenv
from app import en_scrap, jp_scrap

# Results dir
if not os.path.exists(os.getenv("RESULTS_DIR")):
    os.mkdir(os.getenv("RESULTS_DIR"))

def main(params):
    en_scrap.scrap(params)
    jp_scrap.scrap(params)


if __name__ == "__main__":
    # Parse argument
    parser = argparse.ArgumentParser(description="Scrap Arknights Characters Voice and Lines (JP and EN)")
    parser.add_argument("--char_name", required=True, help="Arknights character name")
    parser.add_argument("--url", required=True, help="Arknights wikiru jp character page to scrap JP lines")
    args = parser.parse_args()

    # Run program
    main(args)
import argparse
import os
import time
from urllib import request
from bs4 import BeautifulSoup
from dotenv import load_dotenv; load_dotenv()

URL = "https://arknights.fandom.com/wiki/{}/Dialogue"
VOICE_DIR = os.getenv("VOICE_DIR")
LINE_DIR = os.getenv("LINE_DIR")

if not os.path.exists(VOICE_DIR):
    os.mkdir(VOICE_DIR)

if not os.path.exists(LINE_DIR):
    os.mkdir(LINE_DIR)

def get_html_response(url):
    response = request.urlopen(url)
    return response.read()

def initiate_soup(html):
    return BeautifulSoup(html, "html.parser")

def css_selector(soup, selector):
    return soup.select(selector)

def get_audio_source(elements):
    for elm in elements:
        fn = elm.get("data-mwtitle")
        url = elm.find("source").get("src")
        yield fn, url

def download_audio(url, filename):
    request.urlretrieve(url, filename)


def scrap(params):
    print(f"Running {__name__}")
    # Get page elements
    char_name = params.char_name.title()
    url = URL.format(char_name)
    html = get_html_response(url)
    soup = initiate_soup(html)
    voice_elements = css_selector(soup, "div.mediaContainer > audio")
    line_elements = css_selector(soup, "table.mrfz-wtable tr > td:nth-child(2)")

    # Write char lines
    lvoice_path = os.path.join(LINE_DIR, f"{char_name}_EN.txt")
    if not os.path.exists(lvoice_path):
        with open(lvoice_path, "w") as f:
            f.write("".join(elm.text for elm in line_elements))
    else:
        print(f"{char_name!r} en_lines have already been scrapped!")

    # Make char voice directory
    cvoice_dir = os.path.join(VOICE_DIR, char_name)

    if not os.path.exists(cvoice_dir):
        os.mkdir(cvoice_dir)

        # Download sound in every element found
        for fn, url in get_audio_source(voice_elements):
            file_path = os.path.join(cvoice_dir, fn)
            download_audio(url, file_path)
            print(f"File was saved in {file_path}")
            time.sleep(0.1)
    else:
        print(f"{char_name!r} voices are already been downloaded")

    print(f"{__name__} is finished !")
    
    


if __name__ == "__main__":
    # Parse argument
    parser = argparse.ArgumentParser(description="Scrap Arknights Characters JP_Voice and EN_Lines")
    parser.add_argument("--char_name", required=True, help="Arknights character name")
    args = parser.parse_args()

    # Run Program
    scrap(args)

    
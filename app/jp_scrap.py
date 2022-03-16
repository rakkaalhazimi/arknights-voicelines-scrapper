import argparse
import os
from pathlib import Path
from selenium import webdriver
from dotenv import load_dotenv; load_dotenv()


# Lappland url https://arknights.wikiru.jp/index.php?%A5%E9%A5%C3%A5%D7%A5%E9%A5%F3%A5%C9
HOME_DIR = Path.home()
DRIVER_PATH = os.path.join(HOME_DIR, "chromedriver.exe")
LINE_DIR = os.getenv("LINE_DIR")

if not os.path.exists(LINE_DIR):
    os.mkdir(LINE_DIR)

class LineScrapper:
    def __init__(self, url, char_name):
        # Init variable
        self.url = url
        self.char_name = char_name

        # Initiate websriver options
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"
        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument("--window-size=1920,1080")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument("--disable-extensions")
        options.add_argument("--proxy-server='direct://'")
        options.add_argument("--proxy-bypass-list=*")
        options.add_argument("--start-maximized")
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')

        # Initiate chrome webdriver
        self.driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=options)
        self.driver.get(url)

        # Scrap website
        self.scrap_lines()
        self.driver.quit()

    def scrap_lines(self):
        print(f"Running {__name__}")
        self.driver.find_element_by_id("rgn_button4").click()
        elements = self.driver.find_elements_by_css_selector("#rgn_content4 th.style_th > span")
        path = os.path.join(LINE_DIR, f"{self.char_name}_JP.txt")

        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(elm.text for elm in elements))
        else:
            print(f"{self.char_name!r} jp_lines have already been scrapped!")
        print(f"{__name__} is finished !")


def scrap(params):
    scrapper = LineScrapper(url=params.url, char_name=params.char_name)
    elm = scrapper.scrap_lines()


if __name__ == "__main__":
    # Parse argument
    parser = argparse.ArgumentParser(description="Scrap Arknights Characters JP Lines")
    parser.add_argument("--char_name", required=True, help="Arknights character name")
    parser.add_argument("--url", required=True, help="Arknights wikiru jp character page")
    args = parser.parse_args()

    # Run program
    scrap(args)
    
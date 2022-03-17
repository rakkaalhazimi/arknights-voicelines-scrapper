import os
from pathlib import Path
from urllib import request
from bs4 import BeautifulSoup
from selenium import webdriver

DRIVER_PATH = os.path.join(Path.home(), "chromedriver.exe")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"
SCRAPPER = {}

def add_scrapper(key):
    def scrapper(func):
        SCRAPPER[key] = func
        return
    return scrapper

class WebScrapper:
    def __init__(self, type_):
        assert type_ in SCRAPPER.keys(), "type_ must be one of [{}]".format(", ".join(SCRAPPER.keys()))
        self.type_ = type_
        self.scrapper = SCRAPPER[self.type_]()


@add_scrapper("selenium")
class SeleniumScrapper:
    def __init__(self):
        # Initiate webdriver options
        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument(f'user-agent={USER_AGENT}')
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
        self.url = None
        self.driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=options)


    def switch_url(self, url):
        self.url = url
        self.driver.get(url)

    def get_list(self, selector):
        return self.driver.find_elements_by_css_selector(selector)

    def click(self, selector):
        return self.driver.find_element_by_css_selector(selector).click()

    def quit(self):
        self.driver.quit()


@add_scrapper("bs4")
class Bs4Scrapper:
    def __init__(self):
        self.url = None
        self.response = None
        self.soup = None

    def switch_url(self, url):
        self.url = url
        self.response = request.urlopen(url)
        self.soup = BeautifulSoup(self.response, "html.parser")

    def get_list(self, selector):
        return self.soup.select(selector)


if __name__ == "__main__":
    agent = WebScrapper(url="https://arknights.fandom.com/wiki/Elysium/Dialogue", type_="selenium")
    ...
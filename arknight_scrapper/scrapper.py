from abc import ABC, abstractmethod
import os
import time
import urllib
from urllib import request
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from arknight_scrapper.driver import DefaultWebDriver


RESULTS_DIR="results"
VOICE_DIR="results/voices"
LINE_DIR="results/lines"
OPERATOR_DIR="results/operators"



class Scrapper(ABC):
    @abstractmethod
    def run(self):
        ...

class SeleniumScrapper(Scrapper):
    def __init__(self, headless: bool = True):
        self.driver = DefaultWebDriver(headless=headless).get_driver()
        self.driver.implicitly_wait(2)
        self.action = ActionChains(self.driver)
        self.wait = WebDriverWait(self.driver, 2)

    def scroll_until_bottom(self):
        scroll_tries = 3
        new_diff = -1
        while scroll_tries > 1:
            time.sleep(0.5)
            self.action.send_keys(Keys.PAGE_DOWN).perform()
            last_height = self.driver.execute_script(
                "return window.pageYOffset"
            )
            new_height = self.driver.execute_script(
                "return document.body.scrollHeight"
            )
            last_diff = new_height - last_height

            if new_diff == last_diff:
                scroll_tries -= 1
            else:
                new_diff = last_diff

    def use_search_bar(self, keyword: str, xpath: str):
        search_field = self.wait.until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        search_field.clear()
        search_field.send_keys(keyword)
        search_field.send_keys(Keys.ENTER)
        time.sleep(2)

    def run(self):
        raise NotImplementedError("Implement 'run' method in your own subclass")



class Bs4Scrapper(Scrapper):

    def __init__(self):
        self.soup: BeautifulSoup = None

    def open_url(self, url):
        response = request.urlopen(url)
        return BeautifulSoup(response, "html.parser")

    def get_list(self, selector):
        return self.soup.select(selector)

    def run(self):
        raise NotImplementedError("Implement 'run' method in your own subclass")




class OperatorListScrapper(SeleniumScrapper):

    def run(self):
        text_fn = "operators.txt"
        text_path = os.path.join(OPERATOR_DIR, text_fn)

        if not os.path.exists(OPERATOR_DIR):
            os.makedirs(OPERATOR_DIR, exist_ok=True)

        url_list = [
            "https://arknights.fandom.com/wiki/Operator/6-star",
            "https://arknights.fandom.com/wiki/Operator/5-star",
            "https://arknights.fandom.com/wiki/Operator/4-star",
            "https://arknights.fandom.com/wiki/Operator/3-star",
            "https://arknights.fandom.com/wiki/Operator/2-star",
            "https://arknights.fandom.com/wiki/Operator/1-star",
        ]


        with open(text_path, "w", encoding="utf-8") as file:
            for url in url_list:
                self.driver.get(url)
                time.sleep(1)
                operator_names = self.driver.find_elements_by_css_selector("table.mrfz-wtable > tbody > tr > td:nth-child(2) > a")
                file.write("\n".join(name.text for name in operator_names))
                file.write("\n")

        print(f"Operator list is saved at: {text_path}")
        self.driver.quit()


class OperatorVoiceENScrapper(Bs4Scrapper):

    def run(self):
        main_url = "https://arknights.fandom.com/wiki/{}/Dialogue"
        operator_list_text = os.path.join(OPERATOR_DIR, "operators.txt")

        with open(operator_list_text, "r", encoding="utf-8") as file:
            operators = file.read().splitlines()
            operators = list(filter(lambda text: text, operators))

        if not os.path.exists(VOICE_DIR):
            os.makedirs(VOICE_DIR, exist_ok=True)

        for name in operators:
            # Parse name
            quote_name = urllib.parse.quote(name.replace(" ", "_"))
            url = main_url.format(quote_name)

            # Redirect to url
            try:
                self.soup = self.open_url(url)
            except urllib.error.HTTPError:
                print(f"No link founds for operator {name!r}")
                continue

            # Find elements
            elements = self.get_list(".audio-button audio")
            if not elements:
                print(f"No sound founds for operator {name!r}")
                continue

            # Make char voice directory
            cvoice_dir = os.path.join(VOICE_DIR, name)
            if not os.path.exists(cvoice_dir):
                os.makedirs(cvoice_dir, exist_ok=True)

            # Download sound in every element found
            for elm in elements:
                # Filename
                anchor_tag = elm.find("a")
                anchor_href = anchor_tag.get("href")
                parsed_url = urlparse(anchor_href)

                # format: /wiki/File:Name-001.ogg
                _, fn = parsed_url.path.split(":")
                file_path = os.path.join(cvoice_dir, fn)

                if os.path.exists(file_path):
                    print(f"{file_path!r} are already been downloaded")
                    continue

                # Audio Download
                audio_url = elm.get("src")
                request.urlretrieve(audio_url, file_path)

                # Sleep and report
                print(f"File was saved in {file_path}")
                time.sleep(0.05)
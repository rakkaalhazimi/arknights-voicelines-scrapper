from abc import ABC, abstractmethod
import logging;
import json
import os
import re
import time
import urllib
from urllib import request
from urllib.parse import urlparse, unquote

from bs4 import BeautifulSoup
import cutlet
from selenium.common.exceptions import NoSuchElementException
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

                # format: /wiki/File:<Operator Name>-001.ogg
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


class OperatorListJPScrapper(SeleniumScrapper):
    """
    Scrapper for operator list in japanese.

    In the 'arknights.wikiru.jp', every operators have link to their own profile.
    Each link is referenced by operators name but there are cases when the link
    isn't match with operator name (we will call it 'query name'). The query names
    are needed to visit operator profile page, thus we need to map query name to
    operator name.

    Operator whose query name is found but his real name isn't found might be an unreleased
    opeartor, so we can leave it for now.
    """

    def run(self):
        text_fn = "operators_jp.txt"
        text_path = os.path.join(OPERATOR_DIR, text_fn)

        if not os.path.exists(OPERATOR_DIR):
            os.makedirs(OPERATOR_DIR, exist_ok=True)

        url = "https://arknights.wikiru.jp/?%E3%82%AD%E3%83%A3%E3%83%A9%E3%82%AF%E3%82%BF%E3%83%BC%E4%B8%80%E8%A6%A7"
        self.driver.get(url)
        time.sleep(1)

        # sorttabletable number that aren't shown are operators
        # that haven't been release in global
        tables = [
            "sortabletable1",
            "sortabletable3",
            "sortabletable4",
            "sortabletable5",
            "sortabletable6",
            "sortabletable8",
            "sortabletable9",
            "sortabletable10",
            "sortabletable11",
        ]


        # Get operator url_query and name in japan
        with open(text_path, "w", encoding="utf-8") as text_file:

            for table in tables:
                table_element = self.driver.find_element_by_id(table)
                row_elements = table_element.find_elements_by_css_selector("tbody > tr > td:nth-child(2) > a")

                for row in row_elements:
                    href = row.get_attribute("href")
                    href = unquote(href)

                    operator_name = row.text
                    operator_query = urlparse(href).query

                    # Ignore unreleased operator
                    if operator_name:
                        print("Operator name: ", operator_name)
                        print("Operator query: ", operator_query)
                        print()
                        text_file.write(f"{operator_query}|{operator_name}")
                        text_file.write("\n")


class OperatorVoiceLinesJPScrapper(SeleniumScrapper):
    """
    Scrapper for operator voice lines in japanese.

    Every operator have their own voice lines. We can get operators voiceline by visitting
    their profile page using their query name. The voiceline is located inside a table with
    'rng_content' class name. Unfortunately, it might be placed in any number of `rng_content`
    like 'rng_content1', 'rng_content3', etc. Worry not, we have pre-computed any possibles number.

    Arknight voice line format is leaded by title then the actual line, like 'greet: ohayo dokutah'.
    The titles are written in japanese, so we need to translate them back to EN version. I convert
    the jp line to its latin version because I need that for my deep learning project.
    """
    def run(self):

        main_url = "https://arknights.wikiru.jp/?{}"

        # Operator query name to real name mapper
        with open(os.path.join("data_mapper/jpquery2name.json"), "r", encoding="utf-8") as file:
            query_map = json.load(file)

        # Operator jp to en name mapper
        with open(os.path.join("data_mapper/jp2en.json"), "r", encoding="utf-8") as file:
            en_map = json.load(file)

        # Voice line title map (greetings, idle, etc.)
        with open("data_mapper/jptitle2en.json", "r") as title_map_file:
            jp_title_mapper = json.load(title_map_file)

        # Katsu to convert romaji2latin
        katsu = cutlet.Cutlet(use_foreign_spelling=False)

        # Add exception for こんにちは as it will spit konnichiha
        # instead of konnichiwa.
        # ref: https://github.com/polm/cutlet/issues/33
        katsu.exceptions["こんにちは"] = "konnichiwa"

        jp_line_folder = "jp-test"
        jp_line_dir = os.path.join(LINE_DIR, jp_line_folder)

        if not os.path.exists(jp_line_dir):
            os.makedirs(jp_line_dir, exist_ok=True)

        operator_lines_threshold = 30
        container_element_ids = [
            "rgn_content2",
            "rgn_content3",
            "rgn_content4",
            "rgn_content5",
            "rgn_content6",
            "rgn_content7",
            "rgn_content8",
            "rgn_content9"
        ]

        # Visit each url and retrieve the voice lines
        for query, name in query_map.items():

            # Convert jp name to en name
            en_name = en_map.get(name, name)
            print(f"Fetching {en_name!r} voice lines")

            line_path = os.path.join(jp_line_dir, f"{en_name}.txt")
            if os.path.exists(line_path):
                with open(line_path, "r", encoding="utf-8") as line_file:
                    lines = line_file.readlines()
                    if len(lines) > operator_lines_threshold:
                        print(f"Operator {en_name!r} voice lines has already been downloaded")
                        continue

            # Visit operator profile by query
            url = main_url.format(query)
            self.driver.get(url)

            # Operator voice lines container id is named by arbitrary "rgn_content"
            for element_id in container_element_ids:
                try:
                    container_element = self.driver.find_element_by_id(element_id)
                    voice_lines_table = container_element.find_element_by_tag_name("table")
                    voice_lines_rows = voice_lines_table.find_elements_by_tag_name("tr")

                    if len(voice_lines_rows) < operator_lines_threshold:
                        print(f"{en_name} voice lines is not found in container id {element_id!r}")
                        continue
                    else:
                        break

                except NoSuchElementException:
                    print(f"{en_name} voice lines is not found in container id {element_id!r}")
                    continue


            with open(line_path, "w", encoding="utf-8") as line_file:
                for row_element in voice_lines_rows:
                    title = row_element.find_element_by_css_selector("*:nth-child(1)")
                    lines = row_element.find_element_by_css_selector("*:nth-child(2)")

                    # Somehow, we can't extract text with selenium but BeautifulSoup will do
                    soup_title = BeautifulSoup(title.get_attribute('innerHTML'), "html.parser")
                    soup_lines = BeautifulSoup(lines.get_attribute('innerHTML'), "html.parser")

                    # Jp name is mapped to en name while
                    # romaji line is mapped to its latin version
                    en_title = jp_title_mapper.get(soup_title.text, soup_title.text)
                    romaji_line = soup_lines.text
                    latin_line = katsu.romaji(romaji_line)

                    line_file.write(f"{en_title}|{latin_line}\n")



class OperatorListJP2ENMapScrapper(SeleniumScrapper):

    def run(self):
        main_url = "https://wiki3.jp/arknightsjp/page/14"
        operator_map_fn = "operators_jp2en.txt"
        operator_map_path = os.path.join(OPERATOR_DIR, operator_map_fn)

        if not os.path.exists(OPERATOR_DIR):
            os.makedirs(OPERATOR_DIR, exist_ok=True)

        self.driver.get(main_url)

        operator_rows = self.driver.find_elements_by_css_selector(".equal_width.uk-table > tbody > tr > td")
        print("Operator rows: ", len(operator_rows))

        # JP operator name has format ☆<rank> <operator-name>
        # example: ☆6 エクシア
        #
        # EN operator name has format (<operator-name>)
        # example: (Exusiai)
        #
        operator_star_patterns = "(☆1|☆2|☆3|☆4|☆5|☆6) (.*)"
        operator_latin_patterns = "\((.*)\)"

        with open(operator_map_path, "w", encoding="utf-8") as file:

            for row in operator_rows:
                paragraph_elements = row.find_elements_by_tag_name("p")

                operator_jp_name = ""
                operator_en_name = ""

                for paragraph in paragraph_elements:
                    operator_jp_match = re.search(f"{operator_star_patterns}", paragraph.text)
                    operator_en_match = re.search(f"{operator_latin_patterns}", paragraph.text)

                    if operator_jp_match:
                        operator_jp_name = operator_jp_match.group(2)

                    if operator_en_match:
                        operator_en_name = operator_en_match.group(1)

                    print(paragraph.text)

                print("Operator jp name: ", operator_jp_name)
                print("Operator en name: ", operator_en_name)
                print()
                file.write(operator_jp_name)
                file.write("|")
                file.write(operator_en_name)
                file.write("\n")
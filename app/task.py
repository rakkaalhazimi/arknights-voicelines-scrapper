import os
import urllib.parse
import urllib.error
from urllib import request
import time
from .web_engine import WebScrapper
from .utils import create_directory


__all__ = ["arknight_operator_list", "arknight_operator_lines", "arknight_operator_voices"]


def arknight_operator_list():
    text_dir = os.getenv("OTHER_DIR")
    text_fn = "operators.txt"
    text_path = os.path.join(text_dir, text_fn)

    create_directory(text_dir)

    url_list = [
        "https://arknights.fandom.com/wiki/Operator/6-star",
        "https://arknights.fandom.com/wiki/Operator/5-star",
        "https://arknights.fandom.com/wiki/Operator/4-star",
        "https://arknights.fandom.com/wiki/Operator/3-star",
        "https://arknights.fandom.com/wiki/Operator/2-star",
        "https://arknights.fandom.com/wiki/Operator/1-star",
    ]

    agent = WebScrapper(type_="selenium")

    with open(text_path, "w", encoding="utf-8") as file:
        for url in url_list:
            agent.scrapper.switch_url(url)
            operator_names = agent.scrapper.get_list("table.mrfz-btable > tbody > tr > td:nth-child(2) > a")
            file.write("\n".join(name.text for name in operator_names))

    agent.scrapper.quit()


def arknight_operator_lines():
    main_url = "https://arknights.fandom.com/wiki/{}/Dialogue"
    operator_list_text = os.path.join(os.getenv("OTHER_DIR"), "operators.txt")

    with open(operator_list_text, "r", encoding="utf-8") as file:
        operators = file.read().splitlines()
        operators = list(filter(lambda text: text, operators))

    agent = WebScrapper(type_="bs4")
    line_dir = os.getenv("LINE_DIR")
    create_directory(line_dir)

    for name in operators:
        # Parse name
        quote_name = urllib.parse.quote(name.replace(" ", "_"))
        url = main_url.format(quote_name)

        # Redirect to url
        try:
            agent.scrapper.switch_url(url)
        except urllib.error.HTTPError:
            print(f"No link founds for operator {name!r}")
            continue

        # Find elements
        elements = agent.scrapper.get_list("table.mrfz-wtable tr > td:nth-child(2)")
        if not elements:
            print(f"No lines founds for operator {name!r}")
            continue

        fn = f"{name}_EN.txt"
        file_path = os.path.join(line_dir, fn)

        if not os.path.exists(file_path):
            # Write text in every element found
            with open(file_path, "w", encoding="utf-8") as file:
                file.write("\n".join(elm.text for elm in elements))

        else:
            print(f"{name!r} lines are already been downloaded")


def arknight_operator_lines_jp():
    # self.driver.find_element_by_id(f"rgn_button{self.tag_number}").click()
    # elements = self.driver.find_elements_by_css_selector(f"#rgn_content{self.tag_number} th.style_th > span")
    ...
    

def arknight_operator_voices():
    main_url = "https://arknights.fandom.com/wiki/{}/Dialogue"
    operator_list_text = os.path.join(os.getenv("OTHER_DIR"), "operators.txt")

    with open(operator_list_text, "r", encoding="utf-8") as file:
        operators = file.read().splitlines()
        operators = list(filter(lambda text: text, operators))

    agent = WebScrapper(type_="bs4")
    voice_dir = os.getenv("VOICE_DIR")
    create_directory(voice_dir)

    for name in operators:
        # Parse name
        quote_name = urllib.parse.quote(name.replace(" ", "_"))
        url = main_url.format(quote_name)

        # Redirect to url
        try:
            agent.scrapper.switch_url(url)
        except urllib.error.HTTPError:
            print(f"No link founds for operator {name!r}")
            continue

        # Find elements
        elements = agent.scrapper.get_list(".audio-button audio")
        if not elements:
            print(f"No sound founds for operator {name!r}")
            continue

        # Make char voice directory
        cvoice_dir = os.path.join(os.getenv("VOICE_DIR"), name)
        if not os.path.exists(cvoice_dir):
            os.mkdir(cvoice_dir)

            # Download sound in every element found
            for elm in elements:
                # Filename
                fn = elm.get("data-mwtitle")
                file_path = os.path.join(cvoice_dir, fn)
                
                # Audio Download
                audio_url = elm.find("source").get("src")
                request.urlretrieve(audio_url, file_path)

                # Sleep and report
                print(f"File was saved in {file_path}")
                time.sleep(0.05)
        
        else:
            print(f"{name!r} voices are already been downloaded")


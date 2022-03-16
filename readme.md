# Arknights Voice and Lines Scrap
Scrap and download arknight character voicelines, the voice is mainly JP and the lines are both EN and JP. This project is intended to collect audio data for my deep learning projects, but you can also use it to get your favorite operator voices. Some of the chars can also have no audio link to download, therefore you can specify the url and the css selector in `en_scrap.py` file.

## Requirements
- python==3.5.0 or higher
- chromewebdriver (find [here](https://selenium-python.readthedocs.io/installation.html#introduction) under 1.5 section)
- windows OS (need a bit modification for Linux)

## Installation
1. Clone this repository
   ```
   git clone https://github.com/rakkaalhazimi/arknights-voicelines-scrapper
   ```
2. Pip install requirements.txt
   ```
   pip install -r requirements.txt
   ```
3. Download chrome webdriver [here](https://sites.google.com/chromium.org/driver/) and move it to your home directory (C:/users/username)

4. Make sure your chromewebdriver and your chrome version are match.


## How to Use
The program will scrap voices and english line from https://arknights.fandom.com/ and scrap japan line from https://arknights.wikiru.jp/index.php .

Start scrapping by executing `scrap.py` file with two required arguments, `--char_name` and `--url`.

- --char_name : arknights character name
- --url : url for the specific characters (for japan lines). Find your characters link [here](https://arknights.wikiru.jp/index.php?%A5%AD%A5%E3%A5%E9%A5%AF%A5%BF%A1%BC%B0%EC%CD%F7)

If there is error (it might be because there aren't voice provided for specific chars), you can run the file individually in `app` directory or modify `scrap.py` file.

After scrapping, you can then continue to run `parse.py` with `--char_name` args to convert your scrapped lines into csv file (the results will be stored on `results/csv` dir).

## Projects Info
- Author: Rakka Alhazimi
- Created: 16 March 2022

## Author Notes
This is a hobbyist project yet this automation will be useful in the future if I need to do related projects. If you are also a arknights player, you can add my **id: WeebOverflow#4737**. Thank You :D
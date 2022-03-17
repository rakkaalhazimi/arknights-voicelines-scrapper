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

Start scrapping by executing `scrap.py` file with one required arguments, `--task`.

- --task : what task to be performed? (available: operator_list, operator_lines, operator_voices)

Execute with `--task=operator_list` to get the operator list required for the other task.
(You also need to check the result text first, because there will be a small typo)

After scrapping the operator list, you can then continue to run the other task. Then, you can also run
`parse.py` with `--char_name` args to convert your scrapped lines into csv file (the results will be stored on `results/csv` dir).

## Projects Info
- Author: Rakka Alhazimi
- Created: 16 March 2022

## Author Notes
This is a hobbyist project yet this automation will be useful in the future if I need to do related projects. If you are also a arknights player, you can add my **id: WeebOverflow#4737**. Thank You :D
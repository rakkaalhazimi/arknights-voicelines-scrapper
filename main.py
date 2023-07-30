import argparse
import os
from dotenv import load_dotenv; load_dotenv()
from arknight_scrapper.scrapper import Scrapper, OperatorListScrapper, OperatorVoiceENScrapper


result_dir = os.getenv("RESULTS_DIR")
if not os.path.exists(result_dir):
    os.mkdir(result_dir)



def main(options):

    tasks = {
        "operator_list": OperatorListScrapper(),
        "operator_voices": OperatorVoiceENScrapper(),
        # "operator_lines": arknight_operator_lines,
    }
    scrapper: Scrapper = tasks.get(options.task)
    if scrapper:
        scrapper.run()
    else:
        print("Task is not provided")


if __name__ == "__main__":
    # Parse argument
    parser = argparse.ArgumentParser(description="Arknights Custom WebScrapper, choose your desired task :D.")
    parser.add_argument(
        "task",
        metavar="t",
        help="What task do you want to do? available: [operator_list, operator_voices]"
    )
    # parser.add_argument("--no_headless", default=True, action="store_false", help="Show browser UI when using selenium")
    args = parser.parse_args()

    # Run program
    main(args)
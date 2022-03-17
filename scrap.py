import argparse
import os
from dotenv import load_dotenv; load_dotenv()
from app.task import *
from app.utils import create_directory

# Results dir
create_directory(os.getenv("RESULTS_DIR"))

TASKS = {
    "operator_list": arknight_operator_list,
    "operator_voices": arknight_operator_voices,
    "operator_lines": arknight_operator_lines,
}

def main(params):
    task = TASKS.get(params.task)
    if task:
        task()
    else:
        print("Task is not provided")


if __name__ == "__main__":
    # Parse argument
    parser = argparse.ArgumentParser(description="Arknights Custom WebScrapper, choose your desired task :D.")
    parser.add_argument(
        "--task", 
        required=True, 
        help="What task do you want to do? available:[{}]".format(", ".join(task for task in TASKS.keys()))
    )
    args = parser.parse_args()
    
    # Run program
    main(args)
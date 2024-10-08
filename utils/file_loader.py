import json
import logging
import os


def load_json_file(file_path: str) -> dict:
    """
    Loads a JSON file and returns its contents.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading JSON from file: {file_path} - {e}")
        return {}


def save_results_to_json(results: list, filename: str = "results.json") -> None:
    """
    Saves the provided results to a JSON file.

    This function takes a list of results and saves them to a specified JSON file.
    If no filename is provided, the default filename 'results.json' is used.

    Logs the absolute path of the saved JSON file to the logging system.
    """
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=2)
    log_file_path = os.path.abspath("results.json")
    logging.info(f"Results saved to: file://{log_file_path}")

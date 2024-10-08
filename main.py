import asyncio
import logging

from config import setup_logging
from parsers.github_crawler import GitHubCrawler
from utils.file_loader import load_json_file, save_results_to_json

setup_logging()


async def main():
    """
    The main asynchronous function that initializes the crawler and fetches results.

    The result is saved to a json file.
    """
    logging.info("Starting crawler...")
    data = load_json_file("data.json")
    if not data:
        return
    crawler = GitHubCrawler(**data)
    results = await crawler.crawl()
    save_results_to_json(results)
    logging.info("Finished crawler.")


if __name__ == "__main__":
    asyncio.run(main())

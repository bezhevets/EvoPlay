import asyncio
import json
import logging
import re
import sys
from pprint import pprint

import aiohttp
import random
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    handlers=[
        logging.FileHandler("crawler.log"),
        logging.StreamHandler(sys.stdout)
    ]
)


class ProxyManager:
    def __init__(self, proxies: list) -> None:
        self.proxies = proxies
        self.user_agent = UserAgent()

    def get_random_proxy(self) -> str:
        random_proxy = random.choice(self.proxies)
        return f"http://{random_proxy}"

    def get_headers(self) -> dict:
        return {"user-agent": self.user_agent.random}


class GitHubParser:
    @staticmethod
    async def fetch_url_content(session: aiohttp.ClientSession, url: str, proxy: str, timeout: int=100) -> str | None:
        try:
            async with session.get(url, proxy=proxy, timeout=timeout) as response:
                if response.status == 200:
                    return await response.text()
                return None
        except aiohttp.ClientError as e:
            logging.error(f"Error: {e}. Link: {url}")
            return None

    async def get_languages(self, links: str, session: aiohttp.ClientSession, proxy: str) -> dict:
        content = await self.fetch_url_content(session, links, proxy)
        if not content:
            return {}
        soup = BeautifulSoup(content, 'html.parser')
        languages_blocks = soup.select("div.BorderGrid.about-margin span.Progress span")
        languages = [language.get("aria-label") for language in languages_blocks]
        pattern = r'(\w+)\s([\d.]+)'
        result = {match.group(1): float(match.group(2)) for item in languages if (match := re.match(pattern, item))}
        return result

    async def extra_info_for_repositories(self, links: list, session: aiohttp.ClientSession, proxy: str) -> list:
        parsed_results = []
        for link in links:
            try:
                url, result_dict = link
                owner = result_dict['repo']['repository']['owner_login']
                languages = await self.get_languages(url, session, proxy)
                extra_info = {"url": url, "extra": {"owner": owner, "languages": languages}}
                if not extra_info["extra"]["languages"]:
                    extra_info["extra"]["languages"] = [{result_dict["language"]: None}]
                parsed_results.append(extra_info)
            except KeyError as e:
                logging.error(f"Key error while processing repository: {link} - {e}")
                continue
        return parsed_results

    @staticmethod
    def process_non_repo_links(results: list, search_type: str) -> list:
        if search_type == "issues":
            links = [
                f"/{res['repo']['repository']['owner_login']}/{res['repo']['repository']['name']}/issues/{res['number']}"
                for res in results
            ]
        elif search_type == "wikis":
            links = [
                f"/{res['repo']['repository']['owner_login']}/{res['repo']['repository']['name']}/wiki/{res.get('title').replace(' ', '-')}"
                for res in results
            ]
        else:
            raise ValueError(f"Invalid search type. Search type: {search_type}")
        return [{"url": "https://github.com" + link} for link in links]

    async def parse_html(self, html, session: aiohttp.ClientSession, proxy: str, search_type: str) -> list:
        soup = BeautifulSoup(html, 'html.parser')
        script_tag = soup.select_one("script[data-target='react-app.embeddedData']")
        if script_tag:
            json_data = json.loads(script_tag.text)
            results = json_data.get("payload", {}).get("results", [])
            if search_type == "repositories":
                links = [
                    (f"https://github.com/{re.sub(r'<.*?>', '', result.get('hl_name'))}", result)
                    for result in results
                ]
                parsed_results = await self.extra_info_for_repositories(links, session, proxy)
                return parsed_results
            else:
                return self.process_non_repo_links(results, search_type)
        else:
            logging.info("Failed to parse JSON from HTML.")
            return []


class GitHubCrawler:
    def __init__(self, keywords, proxies, search_type):
        self.keywords = "+".join(keywords)
        self.proxies = proxies
        self.search_type = search_type.lower()
        self.base_url = "https://github.com/search?q={}&type={}"
        self.proxy_manager = ProxyManager(proxies)

    async def fetch_results(self) -> list:
        search_url = self.base_url.format(self.keywords, self.search_type)
        max_retries = len(self.proxies) + 1
        attempts = 0

        while attempts < max_retries:
            proxy = self.proxy_manager.get_random_proxy()
            headers = self.proxy_manager.get_headers()

            async with aiohttp.ClientSession(headers=headers) as session:
                content = await GitHubParser.fetch_url_content(session, search_url, proxy)
                if content:
                    parser = GitHubParser()
                    results = await parser.parse_html(content, session, proxy, self.search_type)
                    return results

            attempts += 1
            logging.info("Retrying with a different proxy/User-Agent.")

        logging.info("Max retries reached. Failed to fetch results.")
        return []

    async def crawl(self) -> list:
        results = await self.fetch_results()
        return results


def load_json_file(file_path: str) -> dict:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading JSON from file: {file_path} - {e}")
        return {}


async def main():
    logging.info("Starting crawler...")
    data = load_json_file("data.json")
    crawler = GitHubCrawler(**data)
    results = await crawler.crawl()
    pprint(results)
    logging.info("Finished crawler.")


asyncio.run(main())

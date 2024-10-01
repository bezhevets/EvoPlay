import asyncio
import json
import re
from pprint import pprint

import aiohttp
import random
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class GitHubCrawler:
    def __init__(self, keywords, proxies, search_type):
        self.keywords = "+".join(keywords)
        self.proxies = proxies
        self.search_type = search_type.lower()
        self.base_url = "https://github.com/search?q={}&type={}"
        self.user_agent = UserAgent()

    @staticmethod
    async def fetch_url_content(session: aiohttp.ClientSession, url: str, proxy: str, timeout=100) -> str | None:
        async with session.get(url, proxy=proxy, timeout=timeout) as response:
            if response.status == 200:
                return await response.text()
            return None

    def get_random_proxy(self) -> str:
        random_proxy = random.choice(self.proxies)
        return f"http://{random_proxy}"

    async def fetch_results(self) -> list | None:
        search_url = self.base_url.format(self.keywords, self.search_type)
        max_retries = len(self.proxies) + 1
        attempts = 0

        while attempts < max_retries:
            headers = {"user-agent": self.user_agent.random}
            proxy = self.get_random_proxy()

            try:
                async with aiohttp.ClientSession(headers=headers) as session:
                    content = await self.fetch_url_content(session, search_url, proxy)
                    if content:
                        print("go")
                        results = await self.parse_html(content, session, proxy)
                        return results
            except aiohttp.ClientError as e:
                print(f"Error: {e}")

            attempts += 1
            print("Retrying with a different proxy/User-Agent.")

        print("Max retries reached. Failed to fetch results.")
        return None

    async def get_languages(self, links: str, session: aiohttp.ClientSession, proxy: str) -> dict:
        content = await self.fetch_url_content(session, links, proxy)
        if content:
            return {}
        soup = BeautifulSoup(content, 'html.parser')
        languages_blocks = soup.select("div.BorderGrid.about-margin span.Progress span")
        languages = [language.get("aria-label") for language in languages_blocks]
        pattern = r'(\w+)\s([\d.]+)'
        result = {match.group(1): float(match.group(2)) for item in languages if (match := re.match(pattern, item))}
        return result

    async def parse_html(self, html, session, proxy):
        soup = BeautifulSoup(html, 'html.parser')
        script_tag = soup.select_one("script[data-target='react-app.embeddedData']")
        if script_tag:
            json_data = json.loads(script_tag.text)
            results = json_data.get("payload", {}).get("results", [])
            pprint(results)
            if self.search_type == "repositories":
                links = [(f"https://github.com/{res.get('hl_name')}", res) for res in results]
                results = []
                for link in links:
                    url = link[0]
                    owner = link[1]['repo']['repository']['owner_login']
                    language = link[1]['language']
                    languages = await self.get_languages(url, session, proxy)
                    extra_info = {"url": url, "extra": {"owner": owner, "languages": languages}}
                    if not extra_info["extra"]["languages"]:
                        extra_info["extra"]["languages"] = [{language: None}]
                    results.append(extra_info)
                return results
            elif self.search_type == "issues":
                links = [
                    f"/{res['repo']['repository']['owner_login']}/{res['repo']['repository']['name']}/issues/{res['number']})"
                    for res in results
                ]
            elif self.search_type == "wikis":
                links = [
                    f"/{res['repo']['repository']['owner_login']}/{res['repo']['repository']['name']}/wiki/{res.get('title').replace(' ', '-')}"
                    for res in results
                ]
            else:
                raise ValueError("Invalid search type")
            return [{"url": "https://github.com" + link} for link in links]
        else:
            print("Failed to parse JSON from HTML.")
            return []

    async def crawl(self) -> list:
        results = await self.fetch_results()
        return results if results else None


async def main():
    crawler = GitHubCrawler(
        keywords=["openstack", "nova", "css"],
        # proxies=["TP88957753:rOjKJlAE@208.195.164.109:65095", "TP65181255:kAYlNkcs@208.195.164.113:65095", "TP22351135:YNrBuIWr@208.195.164.112:65095"],
        proxies=["35.198.189.129:8080"],
        search_type="Repositories"
    )
    results = await crawler.crawl()
    print(results)


asyncio.run(main())

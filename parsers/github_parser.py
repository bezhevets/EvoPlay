import json
import logging
import re
from bs4 import BeautifulSoup
import aiohttp


class GitHubParser:
    @staticmethod
    async def fetch_url_content(session: aiohttp.ClientSession, url: str, proxy: str, timeout: int = 100) -> str | None:
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
        soup = BeautifulSoup(content, "html.parser")
        languages_blocks = soup.select("div.BorderGrid.about-margin span.Progress span")
        languages = [language.get("aria-label") for language in languages_blocks]
        pattern = r"(\w+)\s([\d.]+)"
        result = {match.group(1): float(match.group(2)) for item in languages if (match := re.match(pattern, item))}
        return result

    async def extra_info_for_repositories(self, links: list, session: aiohttp.ClientSession, proxy: str) -> list:
        parsed_results = []
        for link in links:
            try:
                url, result_dict = link
                owner = result_dict["repo"]["repository"]["owner_login"]
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
        soup = BeautifulSoup(html, "html.parser")
        script_tag = soup.select_one("script[data-target='react-app.embeddedData']")
        if script_tag:
            json_data = json.loads(script_tag.text)
            results = json_data.get("payload", {}).get("results", [])
            if search_type == "repositories":
                links = [
                    (f"https://github.com/{re.sub(r'<.*?>', '', result.get('hl_name'))}", result) for result in results
                ]
                parsed_results = await self.extra_info_for_repositories(links, session, proxy)
                return parsed_results
            else:
                return self.process_non_repo_links(results, search_type)
        else:
            logging.info("Failed to parse JSON from HTML.")
            return []

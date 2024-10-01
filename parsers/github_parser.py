import json
import logging
import re
from bs4 import BeautifulSoup
import aiohttp


class GitHubParser:
    """
    Parses HTML content from GitHub search results.
    """

    @staticmethod
    async def fetch_url_content(session: aiohttp.ClientSession, url: str, proxy: str, timeout: int = 100) -> str | None:
        """
        Fetches the content of a URL using a given session and proxy.

        Returns:
            str | None: The response text if successful, or None if the request fails.
        """
        try:
            async with session.get(url, proxy=proxy, timeout=timeout) as response:
                if response.status == 200:
                    return await response.text()
                return None
        except aiohttp.ClientError as e:
            logging.error(f"Error: {e}. Link: {url}")
            return None

    async def get_languages(self, links: str, session: aiohttp.ClientSession, proxy: str) -> dict:
        """
        Extracts programming languages from a repository page.

        Returns:
            dict: A dictionary of programming languages and their usage percentages.
        """
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
        """
        Gathers extra information for a list of repository links.

        Returns:
            list: A list of dictionaries containing the repository URL, owner, and languages.
        """
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
        """
        Processes json (list of dictionaries) to get urls

        Returns:
            list: A list of formatted URLs for issues or wikis.

        Raises:
            ValueError: If the search_type is invalid.
        """
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
        """
        Parses HTML content and extracts relevant information based on the search type.

        Returns:
            list: A list of parsed results.
        """
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

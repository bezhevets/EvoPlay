import logging

import aiohttp

from managers.proxy_manager import ProxyManager
from parsers.github_parser import GitHubParser


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

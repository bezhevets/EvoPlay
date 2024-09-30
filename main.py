import json

import requests
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

    def get_random_proxy(self):
        random_proxy = random.choice(self.proxies)
        return {
            "http": f"http://{random_proxy}",
            "https": f"http://{random_proxy}"
        }

    def fetch_results(self):
        headers = {"user-agent": self.user_agent.random}
        search_url = self.base_url.format(self.keywords, self.search_type)
        proxy = self.get_random_proxy()

        try:
            with requests.get(search_url, headers=headers, proxies=proxy, timeout=100, stream=True) as response:
                if response.status_code == 200:
                    return response.content
                else:
                    print(f"Failed to fetch search results: {response.status_code}")
                    return None
        except requests.exceptions.RequestException as e:
            print(f"Proxy error: {e}")
            return None

    def parse_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        script_tag = soup.select_one("script[data-target='react-app.embeddedData']")
        if script_tag:
            json_data = json.loads(script_tag.text)
            results = json_data.get("payload", {}).get("results", [])
            if self.search_type == "repositories":
                links = [f"/{res.get('hl_name')}" for res in results]
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

    def crawl(self):
        html = self.fetch_results()
        if html:
            return self.parse_html(html)
        return []


crawler = GitHubCrawler(
    keywords=["openstack", "nova", "css"],
    proxies=["TP88957753:rOjKJlAE@208.195.164.109:65095", "TP65181255:kAYlNkcs@208.195.164.113:65095", "TP22351135:YNrBuIWr@208.195.164.112:65095"],
    search_type="wikis"
)

results = crawler.crawl()
print(results)
import random
from fake_useragent import UserAgent


class ProxyManager:
    def __init__(self, proxies: list) -> None:
        self.proxies = proxies
        self.user_agent = UserAgent()

    def get_random_proxy(self) -> str:
        random_proxy = random.choice(self.proxies)
        return f"http://{random_proxy}"

    def get_headers(self) -> dict:
        return {"user-agent": self.user_agent.random}

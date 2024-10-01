import random
from fake_useragent import UserAgent


class ProxyManager:
    """
    Manages proxies and User-Agent headers for the crawler.
    """

    def __init__(self, proxies: list) -> None:
        """
         Initializes the ProxyManager with a list of proxies.

         Args:
             proxies (list): List of proxy addresses.
         """
        self.proxies = proxies
        self.user_agent = UserAgent()

    def get_random_proxy(self) -> str:
        """
        Selects a random proxy from the list.

        Returns:
            str: A random proxy URL.
        """
        random_proxy = random.choice(self.proxies)
        return f"http://{random_proxy}"

    def get_headers(self) -> dict:
        """
        Generates a random User-Agent header.

        Returns:
            dict: A dictionary containing the random User-Agent header.
        """
        return {"user-agent": self.user_agent.random}

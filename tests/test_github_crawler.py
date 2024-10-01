import asyncio
import unittest
from unittest.mock import patch, AsyncMock

from parsers.github_crawler import GitHubCrawler


class TestGitHubCrawler(unittest.TestCase):

    @patch("parsers.github_crawler.ProxyManager.get_random_proxy", return_value="http://proxy.com")
    @patch("parsers.github_crawler.ProxyManager.get_headers", return_value={"User-Agent": "test-agent"})
    @patch("parsers.github_crawler.GitHubParser.fetch_url_content", new_callable=AsyncMock)
    @patch("parsers.github_crawler.GitHubParser.parse_html", new_callable=AsyncMock)
    @patch("aiohttp.ClientSession")
    def test_crawl(
        self, mock_client_session, mock_parse_html, mock_fetch_url_content, mock_get_headers, mock_get_random_proxy
    ):
        mock_fetch_url_content.return_value = "<html></html>"
        mock_parse_html.return_value = [{"url": "https://github.com/repo1"}]

        mock_session_instance = mock_client_session.return_value
        mock_session_instance.__aenter__.return_value = AsyncMock()
        mock_session_instance.__aexit__.return_value = AsyncMock()

        keywords = ["python", "test"]
        proxies = ["http://proxy.com"]
        search_type = "wikis"
        crawler = GitHubCrawler(keywords, proxies, search_type)

        result = asyncio.run(crawler.crawl())

        expected_result = [{"url": "https://github.com/repo1"}]
        self.assertEqual(result, expected_result)

        mock_get_random_proxy.assert_called_once()
        mock_get_headers.assert_called_once()

        mock_fetch_url_content.assert_called_once_with(
            mock_session_instance.__aenter__.return_value,
            crawler.base_url.format(crawler.keywords, crawler.search_type),
            "http://proxy.com",
        )

        mock_parse_html.assert_called_once_with(
            mock_fetch_url_content.return_value,
            mock_session_instance.__aenter__.return_value,
            "http://proxy.com",
            crawler.search_type,
        )

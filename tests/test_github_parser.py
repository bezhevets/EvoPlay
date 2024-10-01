import asyncio
import unittest
from unittest.mock import patch, AsyncMock

from parsers.github_parser import GitHubParser


class TestGitHubParser(unittest.TestCase):
    @patch("parsers.github_crawler.aiohttp.ClientSession")
    @patch.object(GitHubParser, "fetch_url_content", new_callable=AsyncMock)
    def test_fetch_url_content(self, mock_fetch_url_content, mock_session):
        mock_fetch_url_content.return_value = "<html></html>"

        parser = GitHubParser()
        url = "https://github.com"
        proxy = "http://proxy.com"

        result = asyncio.run(parser.fetch_url_content(mock_session, url, proxy))
        self.assertEqual(result, "<html></html>")

    @patch("parsers.github_crawler.GitHubParser.fetch_url_content", new_callable=AsyncMock)
    def test_get_languages(self, mock_fetch_url_content):
        mock_fetch_url_content.return_value = """
        <div class="BorderGrid about-margin" data-pjax>
            <div class="BorderGrid-cell">
                <span class="Progress">
                    <span class="test" aria-label="Python 75.0"></span>
                </span>
                <span class="Progress">
                    <span class="test" aria-label="JavaScript 25.0""></span>
                </span>
            </div>
        </div>
        """
        parser = GitHubParser()
        links = "https://github.com"
        result = asyncio.run(parser.get_languages(links, None, None))

        expected_result = {"Python": 75.0, "JavaScript": 25.0}
        self.assertEqual(result, expected_result)

    @patch("parsers.github_crawler.GitHubParser.get_languages", new_callable=AsyncMock)
    def test_extra_info_for_repositories(self, mock_get_languages):
        mock_get_languages.return_value = {"Python": 75.0}

        parser = GitHubParser()
        links = [
            (
                "https://github.com/user/repo",
                {
                    "repo": {
                        "repository": {
                            "owner_login": "user",
                        }
                    }
                },
            )
        ]

        result = asyncio.run(parser.extra_info_for_repositories(links, None, None))

        expected_result = [
            {"url": "https://github.com/user/repo", "extra": {"owner": "user", "languages": {"Python": 75.0}}}
        ]
        self.assertEqual(result, expected_result)

    @patch("parsers.github_crawler.GitHubParser.fetch_url_content", new_callable=unittest.mock.AsyncMock)
    @patch("parsers.github_crawler.GitHubParser.extra_info_for_repositories", new_callable=unittest.mock.AsyncMock)
    def test_parse_urls_with_html(self, mock_extra_info, mock_fetch_url_content):
        mock_fetch_url_content.return_value = """
            <script data-target="react-app.embeddedData">
            {
                "payload": {
                    "results": [
                        {
                            "hl_name": "<em>repo1</em>",
                            "repo": {
                                "repository": {
                                    "owner_login": "user1"
                                }
                            }
                        },
                        {
                            "hl_name": "<em>repo2</em>",
                            "repo": {
                                "repository": {
                                    "owner_login": "user2"
                                }
                            }
                        }
                    ]
                }
            }
            </script>
            """
        mock_extra_info.return_value = [("https://github.com/repo1", {}), ("https://github.com/repo2", {})]

        parser = GitHubParser()
        search_type = "repositories"
        html = mock_fetch_url_content.return_value

        result = asyncio.run(parser.parse_html(html, None, None, search_type))

        expected_result = [("https://github.com/repo1", {}), ("https://github.com/repo2", {})]

        self.assertEqual(result, expected_result)

    @patch("parsers.github_crawler.GitHubParser.fetch_url_content", new_callable=unittest.mock.AsyncMock)
    def test_parse_html_issues(self, mock_fetch_url_content):
        mock_fetch_url_content.return_value = """
            <script data-target="react-app.embeddedData">
            {
                "payload": {
                    "results": [
                        {
                            "repo": {
                                "repository": {
                                    "owner_login": "user1",
                                    "name": "repo1"
                                }
                            },
                            "number": 123
                        }
                    ]
                }
            }
            </script>
            """
        parser = GitHubParser()
        search_type = "issues"
        html = mock_fetch_url_content.return_value

        result = asyncio.run(parser.parse_html(html, None, None, search_type))

        expected_result = [{"url": "https://github.com/user1/repo1/issues/123"}]
        self.assertEqual(result, expected_result)

    @patch("parsers.github_crawler.GitHubParser.fetch_url_content", new_callable=unittest.mock.AsyncMock)
    def test_parse_html_wikis(self, mock_fetch_url_content):
        mock_fetch_url_content.return_value = """
        <script data-target="react-app.embeddedData">
        {
            "payload": {
                "results": [
                    {
                        "repo": {
                            "repository": {
                                "owner_login": "user2",
                                "name": "repo2"
                            }
                        },
                        "title": "Wiki Page"
                    }
                ]
            }
        }
        </script>
        """
        parser = GitHubParser()
        search_type = "wikis"
        html = mock_fetch_url_content.return_value

        result = asyncio.run(parser.parse_html(html, None, None, search_type))

        expected_result = [{"url": "https://github.com/user2/repo2/wiki/Wiki-Page"}]
        self.assertEqual(result, expected_result)

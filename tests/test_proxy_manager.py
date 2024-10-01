import unittest

from managers.proxy_manager import ProxyManager


class TestProxyManager(unittest.TestCase):
    def setUp(self):
        self.proxy_manager = ProxyManager(["proxy1.com", "proxy2.com"])

    def test_get_random_proxy(self):
        proxy = self.proxy_manager.get_random_proxy()
        self.assertIn(proxy, ["http://proxy1.com", "http://proxy2.com"])

    def test_get_headers(self):
        headers = self.proxy_manager.get_headers()
        self.assertIn("user-agent", headers)

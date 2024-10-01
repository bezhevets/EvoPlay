import unittest
from unittest.mock import patch, mock_open

from utils.file_loader import load_json_file


class TestJsonFunctions(unittest.TestCase):

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""{
        "keywords": ["python", "django-rest-framework", "jwt"],
        "proxies": [
            "TP88957753:rOjKJlAE@208.195.164.109:65095",
            "TP65181255:kAYlNkcs@208.195.164.113:65095",
            "TP22351135:YNrBuIWr@208.195.164.112:65095"
        ],
        "search_type": "Repositories"
    }""",
    )
    def test_load_json_file_success(self, mock_file):
        expected_result = {
            "keywords": ["python", "django-rest-framework", "jwt"],
            "proxies": [
                "TP88957753:rOjKJlAE@208.195.164.109:65095",
                "TP65181255:kAYlNkcs@208.195.164.113:65095",
                "TP22351135:YNrBuIWr@208.195.164.112:65095",
            ],
            "search_type": "Repositories",
        }

        result = load_json_file(mock_file)

        self.assertEqual(result, expected_result)

    @patch("builtins.open", new_callable=mock_open, read_data="not a json")
    def test_load_json_file_invalid_json(self, mock_file):
        with self.assertLogs(level="ERROR") as log:
            result = load_json_file("dummy_path.json")
            self.assertEqual(result, {})
            self.assertIn("Error loading JSON", log.output[0])

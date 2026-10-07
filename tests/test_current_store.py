import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("current_store", ROOT / "scripts/current-store.py")
ops = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ops)


class DeploymentGuards(unittest.TestCase):
    def client(self):
        client = Mock()
        client._config.return_value = ({}, "ath0bu-tg.myshopify.com", "2026-10")
        client.access_scopes.return_value = {"access_scopes": [{"handle": "read_themes"}, {"handle": "write_themes"}]}
        def request(resource):
            if resource == "shop.json":
                return {"shop": {"domain": "boughtitonline.com"}}
            if resource == "themes.json":
                return {"themes": [{"id": 188515188815, "role": "main"}]}
            return {"asset": {"value": "{}"}}
        client.request.side_effect = request
        return client

    def test_wrong_store_refused_before_any_request(self):
        client = self.client()
        client._config.return_value = ({}, "other.myshopify.com", "2026-10")
        with patch.object(ops, "ShopifyClient", return_value=client), patch.object(sys, "argv", ["ops", "status"]):
            with self.assertRaisesRegex(RuntimeError, "Configured store"):
                ops.main()
        client.request.assert_not_called()

    def test_wrong_live_theme_refused_before_write(self):
        client = self.client()
        client.request.side_effect = [{"shop": {"domain": "boughtitonline.com"}}, {"themes": [{"id": 1, "role": "main"}]}]
        with patch.object(ops, "ShopifyClient", return_value=client), patch.object(sys, "argv", ["ops", "status"]):
            with self.assertRaisesRegex(RuntimeError, "Published theme"):
                ops.main()
        client._send.assert_not_called()

    def test_unknown_file_refused_before_write(self):
        client = self.client()
        with patch.object(ops, "ShopifyClient", return_value=client), patch.object(sys, "argv", ["ops", "deploy", "--files", "config/settings_data.json"]):
            with self.assertRaisesRegex(RuntimeError, "allowlist"):
                ops.main()
        client._send.assert_not_called()

    def test_stale_remote_file_refused_before_write(self):
        client = self.client()
        responses = ["main", "abc", "abc", "", '{"sections": {}}']
        with patch.object(ops, "ShopifyClient", return_value=client), patch.object(sys, "argv", ["ops", "deploy", "--files", "templates/index.json"]), patch.object(ops, "git", side_effect=responses), patch.object(ops.subprocess, "run"):
            with self.assertRaisesRegex(RuntimeError, "changed since snapshot"):
                ops.main()
        client._send.assert_not_called()

    def test_line_endings_have_same_digest(self):
        self.assertEqual(ops.digest("line\r\n"), ops.digest("line\n"))


if __name__ == "__main__":
    unittest.main()

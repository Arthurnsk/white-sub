"""Behavior of the merged V2Ray subscription builder."""

import base64
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.update_sub import (
    SOURCES,
    AllSourcesFailed,
    merge_texts,
    update_subscription,
)


class MergeTextsTest(unittest.TestCase):
    def test_keeps_proxy_uris_strips_cr_and_dedupes_by_uri_without_remark(self):
        first = (
            "# comment\r\n"
            "vless://one@host:443?x=1#first\r\n"
            "not-a-proxy\r\n"
            "vmess://abc#keep-me\r\n"
            "  ss://secret#spaced  \r\n"
            "trojan://t#a\n"
            "hysteria2://h#a\n"
            "hy2://h2#a\n"
            "tuic://t2#a\n"
            "http://nope\n"
        )
        second = (
            "vless://one@host:443?x=1#later-remark\n"
            "vmess://abc#other\n"
            "vless://two@host:443#new\n"
            "\n"
        )
        merged = merge_texts([first, None, "", second])
        self.assertEqual(
            merged,
            [
                "vless://one@host:443?x=1#first",
                "vmess://abc#keep-me",
                "ss://secret#spaced",
                "trojan://t#a",
                "hysteria2://h#a",
                "hy2://h2#a",
                "tuic://t2#a",
                "vless://two@host:443#new",
            ],
        )

    def test_preserves_source_order_and_skips_failed_sources(self):
        merged = merge_texts(
            [
                "vless://a#1\n",
                None,
                "vless://b#2\nvless://a#3\n",
            ]
        )
        self.assertEqual(merged, ["vless://a#1", "vless://b#2"])


class UpdateSubscriptionTest(unittest.TestCase):
    def test_writes_plain_list_and_single_line_base64(self):
        bodies = {
            SOURCES[0]: "vless://a#one\r\nvless://b#two\r\n",
            SOURCES[1]: None,
        }

        def fetch(name: str) -> str:
            if name not in bodies or bodies[name] is None:
                raise OSError(f"failed {name}")
            return bodies[name]

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            written = update_subscription(root, fetch)
            sub = (root / "sub.txt").read_bytes()
            b64 = (root / "sub_b64.txt").read_text(encoding="ascii")
            self.assertEqual(written, 2)
            self.assertEqual(sub, b"vless://a#one\nvless://b#two\n")
            self.assertEqual(b64.count("\n"), 1)
            self.assertTrue(b64.endswith("\n"))
            self.assertNotIn("\n", b64.strip())
            self.assertEqual(base64.b64decode(b64.strip()), sub)

    def test_keeps_previous_files_when_result_is_empty(self):
        def fetch(name: str) -> str:
            if name == SOURCES[0]:
                return "# only comments\n\n"
            raise OSError("down")

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sub.txt").write_text("vless://old\n", encoding="utf-8")
            (root / "sub_b64.txt").write_text("previous\n", encoding="ascii")
            written = update_subscription(root, fetch)
            self.assertEqual(written, 0)
            self.assertEqual((root / "sub.txt").read_text(encoding="utf-8"), "vless://old\n")
            self.assertEqual((root / "sub_b64.txt").read_text(encoding="ascii"), "previous\n")

    def test_does_not_create_empty_sub_when_nothing_to_keep(self):
        def fetch(name: str) -> str:
            return ""

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            written = update_subscription(root, fetch)
            self.assertEqual(written, 0)
            self.assertFalse((root / "sub.txt").exists())
            self.assertFalse((root / "sub_b64.txt").exists())

    def test_fails_only_when_every_source_fails(self):
        def fetch(name: str) -> str:
            raise OSError("down")

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sub.txt").write_text("vless://old\n", encoding="utf-8")
            with self.assertRaises(AllSourcesFailed):
                update_subscription(root, fetch)
            self.assertEqual((root / "sub.txt").read_text(encoding="utf-8"), "vless://old\n")


if __name__ == "__main__":
    unittest.main()

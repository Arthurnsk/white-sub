#!/usr/bin/env python3
"""Download public white-list configs and write one merged V2Ray subscription.

Sources come from igareck/vpn-configs-for-russia (branch main). A source that
is empty or fails to download is skipped. The job fails only when every source
fails. An empty merge keeps the previous sub.txt and sub_b64.txt.
"""

from __future__ import annotations

import base64
import sys
import urllib.error
import urllib.request
from pathlib import Path

RAW_BASE = (
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/"
)

SOURCES = (
    "Vless-Reality-White-Lists-Rus-Mobile.txt",
    "Vless-Reality-White-Lists-Rus-Mobile-2.txt",
    "WHITE-CIDR-RU-all.txt",
    "WHITE-CIDR-RU-checked.txt",
    "WHITE-SNI-RU-all.txt",
)

PROXY_SCHEMES = (
    "vless://",
    "vmess://",
    "trojan://",
    "ss://",
    "hysteria2://",
    "hy2://",
    "tuic://",
)

REPO_ROOT = Path(__file__).resolve().parent.parent
TIMEOUT_SECONDS = 60


class AllSourcesFailed(Exception):
    """Every configured source failed to download."""


def proxy_lines(text: str) -> list[str]:
    """Return proxy URI lines from text, with CR characters removed."""
    lines: list[str] = []
    for line in text.replace("\r", "").split("\n"):
        line = line.strip()
        if line.startswith(PROXY_SCHEMES):
            lines.append(line)
    return lines


def dedupe_key(uri: str) -> str:
    """Identity of a proxy URI ignoring the #remark fragment."""
    return uri.split("#", 1)[0]


def merge_texts(texts: list[str | None]) -> list[str]:
    """Merge source bodies. None means that source failed and is skipped."""
    merged: list[str] = []
    seen: set[str] = set()
    for text in texts:
        if not text:
            continue
        for line in proxy_lines(text):
            key = dedupe_key(line)
            if key in seen:
                continue
            seen.add(key)
            merged.append(line)
    return merged


def fetch_source(name: str) -> str:
    """Download one source file. Raises on network or HTTP errors."""
    url = RAW_BASE + name
    request = urllib.request.Request(url, headers={"User-Agent": "white-sub/1.0"})
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        payload = response.read()
    return payload.decode("utf-8", errors="replace")


def update_subscription(root: Path, fetch=fetch_source) -> int:
    """Write sub.txt and sub_b64.txt. Return how many configs were written.

    Returns 0 without touching existing files when the merge is empty.
    Raises AllSourcesFailed when every source fails.
    """
    texts: list[str | None] = []
    failures = 0
    for name in SOURCES:
        try:
            body = fetch(name)
        except (OSError, urllib.error.URLError) as exc:
            failures += 1
            texts.append(None)
            print(f"skip {name}: {exc}", file=sys.stderr)
            continue
        texts.append(body if body else "")
        if not body:
            print(f"skip {name}: empty", file=sys.stderr)

    if failures == len(SOURCES):
        raise AllSourcesFailed("all subscription sources failed")

    merged = merge_texts(texts)
    if not merged:
        print("merge is empty; keeping previous sub.txt", file=sys.stderr)
        return 0

    sub_text = "\n".join(merged) + "\n"
    sub_bytes = sub_text.encode("utf-8")
    b64 = base64.b64encode(sub_bytes).decode("ascii") + "\n"
    (root / "sub.txt").write_bytes(sub_bytes)
    (root / "sub_b64.txt").write_bytes(b64.encode("ascii"))
    print(f"wrote {len(merged)} configs")
    return len(merged)


def main() -> int:
    try:
        update_subscription(REPO_ROOT)
    except AllSourcesFailed as exc:
        print(exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

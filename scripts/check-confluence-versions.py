#!/usr/bin/env python3
"""Check pinned Confluence images against stable Docker Hub tags."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from urllib.parse import urljoin
from pathlib import Path
from typing import Optional


IMAGE_PATTERN = re.compile(r"^\s*image:\s*atlassian/confluence:(\d+\.\d+\.\d+)\s*$")
STABLE_TAG_PATTERN = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
TOKEN_URL = (
    "https://auth.docker.io/token"
    "?service=registry.docker.io&scope=repository:atlassian/confluence:pull"
)
TAGS_URL = "https://registry-1.docker.io/v2/atlassian/confluence/tags/list?n=1000"


def compose_versions(root: Path) -> dict[str, list[tuple[Path, str]]]:
    versions: dict[str, list[tuple[Path, str]]] = {}
    for path in sorted(root.glob("docker-compose.yml*")):
        for line in path.read_text(encoding="utf-8").splitlines():
            match = IMAGE_PATTERN.match(line)
            if match:
                version = match.group(1)
                family = version.rsplit(".", 1)[0]
                versions.setdefault(family, []).append((path, version))
                break
    return versions


def docker_hub_tags() -> set[str]:
    tags: set[str] = set()
    token_request = urllib.request.Request(
        TOKEN_URL, headers={"User-Agent": "confluence-version-checker"}
    )
    with urllib.request.urlopen(token_request, timeout=30) as response:
        token = json.load(response)["token"]

    url: Optional[str] = TAGS_URL
    while url:
        request = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "User-Agent": "confluence-version-checker",
            },
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            page = json.load(response)
            link = response.headers.get("Link")
        tags.update(page.get("tags") or [])
        if link and 'rel="next"' in link:
            url = urljoin(url, link.split(";", 1)[0].strip("<>"))
        else:
            url = None
    return tags


def version_key(version: str) -> tuple[int, int, int]:
    return tuple(map(int, version.split(".")))  # type: ignore[return-value]


def write_outputs(has_updates: bool, report: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as output:
        output.write(f"has_updates={'true' if has_updates else 'false'}\n")
        output.write("report<<CONFLUENCE_REPORT\n")
        output.write(report)
        output.write("\nCONFLUENCE_REPORT\n")


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    current = compose_versions(root)
    if not current:
        print("No atlassian/confluence images were found.", file=sys.stderr)
        return 1

    stable_tags = [tag for tag in docker_hub_tags() if STABLE_TAG_PATTERN.fullmatch(tag)]
    updates: list[tuple[str, str, str, list[Path]]] = []

    for family, entries in sorted(current.items(), key=lambda item: version_key(item[0] + ".0")):
        candidates = [tag for tag in stable_tags if tag.rsplit(".", 1)[0] == family]
        if not candidates:
            continue
        latest = max(candidates, key=version_key)
        installed = min((version for _, version in entries), key=version_key)
        if version_key(latest) > version_key(installed):
            paths = [path for path, version in entries if version_key(version) < version_key(latest)]
            updates.append((family, installed, latest, paths))

    if updates:
        lines = [
            "Docker Hubで、同じリリース系列の新しいConfluence正式版が見つかりました。",
            "",
            "| 系列 | 現在 | 最新 | 対象ファイル |",
            "|---|---:|---:|---|",
        ]
        for family, installed, latest, paths in updates:
            filenames = "<br>".join(f"`{path.name}`" for path in paths)
            lines.append(f"| {family} | {installed} | {latest} | {filenames} |")
        lines.extend(["", "このIssueは確認通知です。ファイルの自動更新や自動マージは行いません。"])
        report = "\n".join(lines)
    else:
        report = "すべてのConfluenceイメージが、設定されている各リリース系列の最新版です。"

    print(report)
    write_outputs(bool(updates), report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

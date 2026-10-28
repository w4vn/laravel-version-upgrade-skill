#!/usr/bin/env python3
"""Verify the pinned official snapshots against upstream. Network required; writes nothing.

For every manifest entry this checks that
  1. the URL is the immutable raw URL for exactly the recorded repository and commit,
  2. the file at that URL matches the recorded SHA-256 and size, and
  3. the commit is reachable from the official branch named by the entry's `version`
     (for example `13.x` or `5.8`). This rejects commits that exist only in a fork:
     GitHub serves fork commits through the parent repository's raw URLs.

Usage: python3 -I tools/verify_sources.py [manifest.json]
Set GITHUB_TOKEN to raise the GitHub API rate limit (CI does).
"""
import concurrent.futures
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT = Path(__file__).resolve().parents[1] / "skills/laravel-upgrade/references/source-manifest.json"
REPOSITORIES = {"laravel/docs", "laravel/framework"}


def get(url, api=False):
    headers = {"User-Agent": "verify-sources"}
    if api:
        headers["Accept"] = "application/vnd.github+json"
        if os.environ.get("GITHUB_TOKEN"):
            headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as response:
        return response.read()


def ancestry(repository, branch, commit):
    try:
        data = json.loads(get(f"https://api.github.com/repos/{repository}/compare/{branch}...{commit}", api=True))
    except urllib.error.HTTPError as error:
        hint = "; rate limited, set GITHUB_TOKEN" if error.code in (403, 429) else ""
        return f"compare failed (HTTP {error.code}{hint})"
    return None if data.get("status") in ("behind", "identical") else f"not on branch {branch} ({data.get('status')})"


def verify(record, cache):
    repository, commit, path = record["repository"], record["commit"], record["path"]
    if repository not in REPOSITORIES:
        return path, f"repository {repository} is not allowed"
    parts = Path(path).parts
    if len(parts) == 3 and parts[1] != record["version"]:
        return path, f"stored under {parts[1]} but pinned to version {record['version']}"
    if not record["url"].startswith(f"https://raw.githubusercontent.com/{repository}/{commit}/"):
        return path, "URL does not match repository and commit"
    try:
        data = get(record["url"])
    except Exception as error:  # report, keep checking the rest
        return path, f"download failed: {error}"
    if hashlib.sha256(data).hexdigest() != record["sha256"] or len(data) != record["bytes"]:
        return path, "content differs from the pinned upstream file"
    key = (repository, record["version"], commit)
    if key not in cache:
        cache[key] = ancestry(*key)
    return path, cache[key]


def main():
    manifest = json.loads(Path(sys.argv[1] if len(sys.argv) > 1 else DEFAULT).read_text(encoding="utf-8"))
    cache = {}
    with concurrent.futures.ThreadPoolExecutor(8) as pool:
        results = list(pool.map(lambda record: verify(record, cache), manifest["files"]))
    failures = [(path, problem) for path, problem in results if problem]
    print(f"{len(results) - len(failures)}/{len(results)} official files verified (content and branch provenance)")
    for path, problem in failures:
        print(f"  FAIL {path}: {problem}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

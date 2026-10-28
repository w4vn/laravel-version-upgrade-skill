#!/usr/bin/env python3
"""Pin one official upstream file into references/official and append its manifest entry.

Usage: python3 -I tools/add_snapshot.py <laravel/docs|laravel/framework> <40-char commit> <remote path> <local path under official/> <version> <ref description>
"""
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "skills/laravel-upgrade/references"


def main(argv):
    if len(argv) != 6:
        sys.exit(__doc__)
    repository, commit, remote, local, version, description = argv
    if repository not in {"laravel/docs", "laravel/framework"}:
        sys.exit("Only laravel/docs and laravel/framework are allowed")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        sys.exit("Commit must be a full 40-character SHA (resolve branches/tags first)")
    target = (ROOT / "official" / local).resolve()
    if not target.is_relative_to((ROOT / "official").resolve()) or ".." in Path(local).parts:
        sys.exit("Local path must stay inside references/official")
    if target.exists():
        sys.exit(f"Refusing to overwrite {local}; delete it and its manifest entry deliberately first")
    url = f"https://raw.githubusercontent.com/{repository}/{commit}/{remote.lstrip('/')}"
    request = urllib.request.Request(url, headers={"User-Agent": "add-snapshot"})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read()
    manifest_path = ROOT / "source-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    path = f"official/{local}"
    if any(record["path"] == path for record in manifest["files"]):
        sys.exit(f"Manifest already lists {path}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    manifest["files"].append({"repository": repository, "commit": commit, "version": version,
                              "ref_description": description, "url": url, "path": path,
                              "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(f"Pinned {path} ({len(data)} bytes) from {url}")


if __name__ == "__main__":
    main(sys.argv[1:])

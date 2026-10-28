#!/usr/bin/env python3
"""Static Laravel upgrade inventory. No project execution, network, or writes."""
import argparse
from bisect import bisect_right
from decimal import Decimal
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys

HOPS = [f"5.{n}" for n in range(9)] + [str(n) for n in range(6, 14)]
SKIP = {"vendor", "node_modules", ".git", "storage", "public", "build", "dist",
        ".tokensave", "graphify-out", ".idea", ".vscode", "__pycache__"}
HELPERS = """array_add array_collapse array_divide array_dot array_except array_first
array_flatten array_forget array_get array_has array_last array_only array_pluck
array_prepend array_pull array_random array_set array_sort array_sort_recursive
array_where array_wrap camel_case ends_with kebab_case snake_case starts_with
str_after str_before str_contains str_finish str_is str_limit str_plural str_random
str_replace_array str_replace_first str_replace_last str_singular str_slug str_start
studly_case title_case""".split()
SIMPLE_ARG = r"(?:'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"|\$[A-Za-z_]\w*(?:->[A-Za-z_]\w*)?|-?\d+(?:\.\d+)?|true|false|null)"
PATTERNS = {
    "legacy_input_facade": r"\bInput::",
    "model_dates": r"\$dates\s*=",
    "legacy_factory": r"\bfactory\s*\(|\$factory->",
    "swift_mailer": r"Swift_|withSwiftMessage|swiftmailer",
    "dispatch_now": r"\bdispatchNow\s*\(",
    "schema_change": r"->change\s*\(",
    "carbon_difference": r"->(?:diffIn\w+|floatDiffIn\w+|diffForHumans)\s*\(",
    "uuid_generation": r"\bHasUuids\b|\bHasVersion[47]Uuids\b",
    "request_get": r"\$request->get\s*\(|\bRequest::get\s*\(",
    "env_outside_config": r"\benv\s*\(",
    "proxy_and_csrf": r"fideloper|TrustProxies|VerifyCsrfToken|PreventRequestForgery",
    "serialization": r"(?<![\w.])(?<!->)(?<!::)(?:unserialize|serialize)\s*\(|\bfunction\s+serializeDate\s*\(",
    "pdf_and_spreadsheet": r"\b(?:Dompdf|PDF|Excel)::|PhpSpreadsheet|PhpWord",
    "external_delivery": r"\b(?:Mail|Notification|Storage|Http)::|\bGuzzleHttp\\",
    "queue_and_schedule": r"ShouldQueue|withoutOverlapping|onOneServer|->afterCommit\s*\(",
    "php85_array_helpers": r"(?<![\w.])(?<!->)(?<!::)\b(?:array_first|array_last)\s*\(",
    "upsert_unique_by": r"(?:->|::)\s*upsert\s*\(",
    "csrf_middleware_exclusions": r"\bwithoutMiddleware\s*\([^;)]{0,1500}\b(?:VerifyCsrfToken|ValidateCsrfToken)\b[^;)]{0,1500}\)",
    "exception_handler_signatures": r"\bfunction\s+(?:report|render)\s*\([^)]{0,1000}?(?<![\w\\])\\?Exception\s+\$\w+",
    "blade_or_default": r"\{\{(?:(?!\}\}).){0,1000}?\s+or\s+(?:(?!\}\}).){0,1000}?\}\}",
    "cache_integer_ttl": rf"\bCache::(?:(?:put|add)\s*\(\s*{SIMPLE_ARG}\s*,\s*{SIMPLE_ARG}\s*,\s*[+-]?\d+\s*(?=[,)])|remember\s*\(\s*{SIMPLE_ARG}\s*,\s*[+-]?\d+\s*,)",
}
CONTENT_KEYS = ("name", "version", "require", "require-dev", "conflict", "replace", "provide",
                "minimum-stability", "prefer-stable", "repositories", "extra")


def read_json(path, required=False):
    if path.is_symlink():
        raise ValueError(f"Refusing symlinked metadata: {path.name}")
    if not path.exists():
        if required:
            raise ValueError(f"Missing {path.name}; pass the application directory")
        return None
    if path.stat().st_size > 16_000_000:
        raise ValueError(f"Metadata exceeds 16 MB limit: {path.name}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object: {path.name}")
    return data


def php_json_encode(value):
    """Composer's PHP json_decode(..., true), then json_encode(..., 0), on 64-bit PHP."""
    if value is None or isinstance(value, bool):
        return json.dumps(value)
    if isinstance(value, str):
        value.encode("utf-8")  # Reject lone surrogates just as PHP JSON decoding does.
        return json.dumps(value, ensure_ascii=True).replace("/", "\\/")
    if isinstance(value, int) and not -(2**63) <= value < 2**63:
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Non-finite number in Composer metadata")
        if value == 0:
            return "-0" if math.copysign(1, value) < 0 else "0"
        text = repr(value).lower()
        if 1e-4 <= abs(value) < 1e17:
            text = format(Decimal(text), "f")
            return text[:-2] if text.endswith(".0") else text
        mantissa, exponent = text.split("e")
        if "." not in mantissa:
            mantissa += ".0"
        exponent = int(exponent)
        return f"{mantissa}e{'+' if exponent >= 0 else ''}{exponent}"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, dict):
        converted = {}
        for key, item in value.items():
            numeric = re.fullmatch(r"-?(?:0|[1-9][0-9]*)", key)
            if numeric and str(int(key)) == key and -(2**63) <= int(key) < 2**63:
                key = int(key)
            converted[key] = item
        if list(converted) == list(range(len(converted))):
            return "[" + ",".join(php_json_encode(item) for item in converted.values()) + "]"
        return "{" + ",".join(php_json_encode(str(key)) + ":" + php_json_encode(item)
                               for key, item in converted.items()) + "}"
    if isinstance(value, list):
        return "[" + ",".join(php_json_encode(item) for item in value) + "]"
    raise ValueError("Unsupported value in Composer metadata")


def content_hash(manifest):
    relevant = {key: manifest[key] for key in CONTENT_KEYS if key in manifest}
    platform = manifest.get("config", {}).get("platform")
    if platform is not None:
        relevant["config"] = {"platform": platform}
    encoded = php_json_encode(dict(sorted(relevant.items())))
    return hashlib.md5(encoded.encode("utf-8")).hexdigest()


def version_value(value):
    if isinstance(value, bool):
        return value
    text = str(value)
    return "[non-version value omitted]" if re.search(r"[/@:]", text) else text


def constraints(values):
    if not isinstance(values, dict):
        raise ValueError("Expected dependency constraints to be an object")
    return {name: version_value(value) for name, value in sorted(values.items())}


def hop_path(locked_version, target):
    match = re.fullmatch(r"v?(\d+)\.(\d+)(?:\.\d+)?(?:[-+][\w.-]+)?", locked_version or "")
    if not match:
        return None
    current = f"5.{match[2]}" if match[1] == "5" else match[1]
    if current not in HOPS or target not in HOPS:
        return None
    start, end = HOPS.index(current), HOPS.index(target)
    if end < start:
        raise ValueError("Target is older than locked Laravel; this is not a downgrade tool")
    return HOPS[start:end + 1]


def compiled_patterns(framework=None, locked_names=()):
    helpers = [name for name in HELPERS if name not in {"array_first", "array_last"}]
    version = re.match(r"v?(\d+)\.(\d+)", framework or "")
    if version and int(version[1]) >= 6 and "laravel/helpers" not in locked_names:
        helpers.remove("str_contains")
    patterns = dict(PATTERNS)
    if not version or (int(version[1]), int(version[2])) >= (5, 7):
        patterns["blade_or_default"] = r"(?!)"
    patterns["legacy_helpers"] = r"(?<![\w.])(?<!->)(?<!::)\b(?:" + "|".join(helpers) + r")\s*\("
    return {name: re.compile(pattern, re.DOTALL) for name, pattern in patterns.items()}


def scan(root, framework=None, locked_names=()):
    patterns = compiled_patterns(framework, locked_names)
    findings = {name: {"matched_lines": 0, "examples": []} for name in patterns}
    scanned, warnings, seen = 0, [], set()
    # ponytail: bounded regex hints, not PHP analysis; trace callers before fixes.
    for folder in ("app", "routes", "database", "config", "bootstrap", "tests",
                   "resources/views", "Modules", "modules", "packages"):
        base = root / folder
        if any(p.is_symlink() for p in (base, *base.parents) if p != root and root in p.parents):
            warnings.append(f"Skipped symlinked source directory: {folder}")
            continue
        if not base.exists():
            continue
        def on_error(error):
            warnings.append(f"Unreadable directory: {Path(error.filename).name}")
        for directory, dirs, files in os.walk(base, followlinks=False, onerror=on_error):
            dirs[:] = sorted(d for d in dirs if d not in SKIP and not d.startswith(".")
                             and not (Path(directory).name == "bootstrap" and d == "cache")
                             and not (Path(directory) / d).is_symlink())
            for name in sorted(files):
                path = Path(directory) / name
                if not name.endswith(".php") or path.is_symlink():
                    continue
                relative = path.relative_to(root).as_posix()
                info = path.stat()
                identity = (info.st_dev, info.st_ino)
                if identity in seen:
                    continue
                seen.add(identity)
                if scanned >= 10000:
                    warnings.append("Reached 10000-file limit; source scan is incomplete")
                    return {"files": scanned, "warnings": warnings, "hints": findings}
                if info.st_size > 2_000_000:
                    warnings.append(f"Skipped file over 2 MB: {relative}")
                    continue
                try:
                    text = path.read_text(encoding="utf-8")
                except (OSError, UnicodeError):
                    warnings.append(f"Unreadable source: {relative}")
                    continue
                scanned += 1
                newlines = [match.start() for match in re.finditer("\n", text)]
                blade_text = re.sub(r"\{\{--.*?(?:--\}\}|$)",
                                    lambda match: re.sub(r"[^\r\n]", " ", match[0]), text, flags=re.DOTALL)
                for label, pattern in patterns.items():
                    if label == "env_outside_config" and folder == "config":
                        continue
                    if label == "exception_handler_signatures" and name != "Handler.php":
                        continue
                    if label == "blade_or_default" and not name.endswith(".blade.php"):
                        continue
                    source = blade_text if label == "blade_or_default" else text
                    numbers = sorted({bisect_right(newlines, match.start()) + 1 for match in pattern.finditer(source)})
                    result = findings[label]
                    result["matched_lines"] += len(numbers)
                    result["examples"].extend(f"{relative}:{number}" for number in numbers[:12 - len(result["examples"])])
    return {"files": scanned, "warnings": warnings, "hints": findings}


def runtime_files(root):
    files, warnings, examined = [], [], 0
    metadata = {".php-version", ".tool-versions", "phpunit.xml", "phpunit.xml.dist",
                "phpstan.neon", "phpstan.neon.dist", "rector.php", "rector.php.dist",
                ".gitlab-ci.yml", "bitbucket-pipelines.yml", "deploy.php", "Envoy.blade.php"}
    def on_error(error):
        warnings.append(f"Unreadable runtime directory: {Path(error.filename).name}")
    for directory, dirs, names in os.walk(root, followlinks=False, onerror=on_error):
        relative_dir = Path(directory).relative_to(root)
        depth = len(relative_dir.parts)
        dirs[:] = sorted(d for d in dirs if depth < 2 and d not in SKIP
                         and (not d.startswith(".") or (depth == 0 and d == ".github"))
                         and not (Path(directory).name == "bootstrap" and d == "cache")
                         and not (Path(directory) / d).is_symlink())
        for name in sorted(names):
            examined += 1
            if examined > 10000:
                warnings.append("Runtime discovery reached 10000-file limit")
                return sorted(files), warnings
            path = Path(directory) / name
            if path.is_symlink() or name in {"composer.json", "composer.lock"}:
                continue
            relative = path.relative_to(root).as_posix()
            dockerfile = name.startswith("Dockerfile")
            compose = re.fullmatch(r"(?:compose(?:\.[^.]+)*|docker-compose[^/]*)\.ya?ml", name)
            if not (dockerfile or compose or name in metadata or relative.startswith(".github/workflows/")):
                continue
            if dockerfile:
                if path.stat().st_size > 2_000_000:
                    warnings.append(f"Skipped Dockerfile over 2 MB: {relative}")
                    continue
                try:
                    lines = path.read_text(encoding="utf-8").splitlines()
                except (OSError, UnicodeError):
                    warnings.append(f"Unreadable Dockerfile: {relative}")
                    continue
                from_lines = [line.strip() for line in lines if re.match(r"\s*FROM\s+", line, re.I)]
                from_lines = ["[credential-bearing FROM omitted]" if re.search(r"://|\S+:\S+@", line) else line
                              for line in from_lines]
                files.append(relative + (" (" + "; ".join(from_lines) + ")" if from_lines else " (no FROM found)"))
            else:
                files.append(relative)
    return sorted(files), warnings


def inventory(root, target="13", with_scan=False, brief=False):
    root = Path(root).expanduser().resolve()
    manifest = read_json(root / "composer.json", required=True)
    lock = read_json(root / "composer.lock")
    packages, framework = [], None
    direct_names = set(manifest.get("require", {})) | set(manifest.get("require-dev", {}))
    for group in ("packages", "packages-dev"):
        for package in (lock or {}).get(group, []):
            framework_requirements = {}
            for name, constraint in sorted(package.get("require", {}).items()):
                if name.startswith("illuminate/") or name == "laravel/framework":
                    framework_requirements.setdefault(constraint, []).append(name)
            row = {"name": package["name"], "version": version_value(package["version"]),
                   "dev": group == "packages-dev",
                   "php": version_value(package.get("require", {}).get("php", "unspecified")),
                   "abandoned": bool(package.get("abandoned", False)),
                   "framework_requirements": framework_requirements}
            packages.append(row)
            if row["name"] == "laravel/framework":
                framework = row["version"]
    config = manifest.get("config", {})
    computed_hash = content_hash(manifest)
    locked_hash = (lock or {}).get("content-hash")
    in_sync = locked_hash == computed_hash if isinstance(locked_hash, str) and re.fullmatch(r"[a-f0-9]{32}", locked_hash) else None
    runtime, runtime_warnings = runtime_files(root)
    node = read_json(root / "package.json") or {}
    report = {
        "root": str(root), "mode": "static-read-only", "target": target,
        "framework_constraint": constraints(manifest.get("require", {})).get("laravel/framework"),
        "framework_locked": framework,
        "dependency_confidence": "repository-locked" if framework else "unknown-no-framework-lock",
        "production_parity": "unverified", "vendor_consistency": "not-inspected",
        "lock_sha256": hashlib.sha256((root / "composer.lock").read_bytes()).hexdigest() if lock is not None else None,
        "lock_in_sync": in_sync, "lock_content_hash": locked_hash, "computed_content_hash": computed_hash,
        "require": constraints(manifest.get("require", {})),
        "require_dev": constraints(manifest.get("require-dev", {})),
        "platform": constraints(config.get("platform", {})),
        "composer_script_names": sorted(manifest.get("scripts", {})),
        "composer_plugin_policy_present": "allow-plugins" in config,
        "locked_packages": packages,
        "root_requirements_without_named_lock_entry": sorted(
            name for name in {**manifest.get("require", {}), **manifest.get("require-dev", {})}
            if "/" in name and name not in {p["name"] for p in packages}),
        "hop_path": hop_path(framework, target),
        "runtime_files_to_review": runtime, "runtime_scan_warnings": runtime_warnings,
        "node_dependencies": constraints(node.get("dependencies", {})),
        "node_dev_dependencies": constraints(node.get("devDependencies", {})),
        "limitations": ["No PHP, Composer, Artisan, tests, project scripts, or network were executed.",
                        "No .env, credentials, database contents, or arbitrary source/config values are emitted; Dockerfile output is FROM lines only.",
                        "Content hash matches Composer's selected metadata on 64-bit PHP with default serialize_precision=-1; it is not vendor or production evidence.",
                        "Missing named lock entries are hints: provide/replace and constraint satisfaction need separate review.",
                        "Regex hints are bounded, not PHP parsing; integer TTL detection covers simple literal/variable arguments, not all wrappers or expressions.",
                        "PHP/extension compatibility, security advisories and package support require separate verification."],
    }
    if brief:
        retained = [package for package in packages if package["name"] in direct_names
                    or package["abandoned"] or package["framework_requirements"]]
        report["locked_packages"] = retained
        report["package_summary"] = {"output": "brief", "total_locked": len(packages),
                                     "reported_locked": len(retained), "omitted_locked": len(packages) - len(retained)}
        report["limitations"].append("Brief mode omits other transitive packages; use the complete lock/package list for advisory coverage.")
    if with_scan:
        report["source_scan"] = scan(root, framework, {package["name"] for package in packages})
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", help="Application directory containing composer.json")
    parser.add_argument("--target", choices=HOPS, default="13")
    parser.add_argument("--scan", action="store_true", help="Add bounded static PHP hints (not confirmed defects)")
    parser.add_argument("--brief", action="store_true", help="Keep direct, abandoned and framework-constrained locked packages only")
    args = parser.parse_args()
    try:
        print(json.dumps(inventory(args.root, args.target, args.scan, args.brief), indent=2, ensure_ascii=False))
    except (OSError, ValueError, KeyError, TypeError, AttributeError, OverflowError) as error:
        print(f"Inventory failed: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Offline checks for inventory, JUnit comparison, skill links and local snapshots."""
import argparse
from datetime import datetime
import hashlib
import os
import json
from pathlib import Path
import re
import runpy
import shlex
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
API = runpy.run_path(str(ROOT / "scripts/inventory.py"))
JUNIT = runpy.run_path(str(ROOT / "scripts/compare_junit.py"))
HOPS = API["HOPS"]


def validate_plan_history(state_path, invocation_source=None):
    """Check recorded approval/version/hash consistency, not human authenticity or app readiness."""
    state_path = Path(state_path).expanduser().resolve()
    if state_path.stat().st_size > 2_000_000:
        raise ValueError("Run-state exceeds 2 MB")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if state.get("schema_version") != 2:
        raise ValueError("Plan history requires schema 2; approve migration without resetting progress/counters")

    def absolute(value):
        path = Path(value).expanduser()
        if not path.is_absolute():
            raise ValueError("Plan sources, repository and worktree paths must be absolute or home-relative (~/...)")
        return path.resolve()

    workspace = absolute(state["workspace"]["path"])
    repository = absolute(state["project"]["root_path"])
    if state_path != workspace / "docs/upgrade/run-state.json":
        raise ValueError("Run-state does not belong to its recorded worktree")

    def copied(value):
        path = Path(value)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("Plan copies must be relative paths inside the worktree")
        path = (workspace / path).resolve()
        if not path.is_relative_to(workspace / "docs/upgrade"):
            raise ValueError("Plan copy escapes docs/upgrade")
        return path

    def digest(path):
        if not path.is_file():
            raise ValueError("Plan source/copy must be a regular file")
        with path.open("rb") as stream:
            data = stream.read(4_000_001)
        if len(data) > 4_000_000:
            raise ValueError("Plan exceeds 4 MB")
        return hashlib.sha256(data).hexdigest()

    approvals = state["approvals"]
    invocation = approvals["range_invocation"]
    decisions = [invocation] + approvals.get("decisions", [])
    records = {row["id"]: row for row in decisions}
    if len(records) != len(decisions):
        raise ValueError("Duplicate approval identities")
    history = state["plan_versions"]
    if not isinstance(history, list) or not 1 <= len(history) <= 100:
        raise ValueError("Missing or oversized plan-version history")
    sources, copies = set(), set()
    for number, version in enumerate(history, 1):
        if version["version"] != number or not re.fullmatch(r"[a-f0-9]{64}", version["sha256"]):
            raise ValueError("Invalid plan version sequence or SHA-256")
        source, copy = absolute(version["source_path"]), copied(version["copy_path"])
        if source.is_relative_to(repository) or source.is_relative_to(workspace):
            raise ValueError("Durable source plan must be outside the repository and upgrade worktree")
        if source in sources or copy in copies:
            raise ValueError("Each approved version needs new immutable source and archive paths")
        sources.add(source)
        copies.add(copy)
        record = records.get(version["approval_ref"])
        if record is None or record.get("plan_sha256") != version["sha256"]:
            raise ValueError("Plan revision has no matching recorded user approval")
        approved_at = version["approved_at"]
        if datetime.fromisoformat(approved_at.replace("Z", "+00:00")).tzinfo is None:
            raise ValueError("Approval timestamps need a timezone")
        if number == 1:
            if (record is not invocation or record.get("kind") != "range-command"
                    or record.get("invoked_at") != approved_at
                    or absolute(record["plan_source_path"]) != source
                    or not record.get("command", "").startswith("/laravel-upgrade-step ")):
                raise ValueError("Initial plan must be bound to the user's recorded range invocation")
        elif (record.get("kind") != "user-decision" or record.get("approved_at") != approved_at
              or not isinstance(record.get("user_response"), str) or not record["user_response"].strip()
              or not isinstance(record.get("redactions"), list)):
            raise ValueError("A revised plan requires the user's decision text or explicitly redacted text")
        if digest(source) != version["sha256"] or digest(copy) != version["sha256"]:
            raise ValueError(f"Plan version {number} source/archive changed without matching approved history")
    current, latest = state["approved_plan"], history[-1]
    if (current["path"] != "docs/upgrade/plan.md" or current["version"] != latest["version"]
            or current["sha256"] != latest["sha256"]
            or absolute(current["source_path"]) != absolute(latest["source_path"])
            or digest(copied(current["path"])) != latest["sha256"]):
        raise ValueError("Active plan source/copy/hash is not the latest approved version")
    if invocation_source is not None and absolute(invocation_source) not in sources:
        raise ValueError("The invoked plan path is not in this run's approved history")
    return latest["version"]


def hash_checks():
    # Golden encodings cross-checked with isolated PHP json_decode(..., true)/json_encode(..., 0).
    escaped_label = chr(92) + "u65e5"
    escaped_emoji = chr(92) + "ud83d" + chr(92) + "ude00"
    cases = [({}, "[]"), ({"0": "a"}, '["a"]'),
             ({"0": "a", "1": "b"}, '["a","b"]'),
             ({"1": "b", "0": "a"}, '{"1":"b","0":"a"}'),
             ({"00": "a", "-0": "b"}, '{"00":"a","-0":"b"}'),
             ({"0": {}}, "[[]]"), ("日😀", '"' + escaped_label + escaped_emoji + '"'),
             ("https://example.test/a/b", r'"https:\/\/example.test\/a\/b"'),
             (1.0, "1"), (-0.0, "-0"), (1e-5, "1.0e-5"), (1e-4, "0.0001"),
             (1e16, "10000000000000000"), (1e17, "1.0e+17"),
             (9223372036854775808, "9.223372036854776e+18")]
    for value, expected in cases:
        assert API["php_json_encode"](value) == expected, (value, expected)
    manifest = {"require": {"vendor/b": "^2", "vendor/a": "^1"}, "name": "vendor/demo",
                "extra": {"label": "日", "empty": {}},
                "config": {"platform": {"php": "7.4.33"}, "sort-packages": True},
                "scripts": {"test": "NEVER_EXECUTE"}, "autoload": {"files": ["never.php"]}}
    encoded = r'{"config":{"platform":{"php":"7.4.33"}},"extra":{"label":"<label>","empty":[]},"name":"vendor\/demo","require":{"vendor\/b":"^2","vendor\/a":"^1"}}'.replace("<label>", escaped_label)
    expected = hashlib.md5(encoded.encode()).hexdigest()
    assert API["content_hash"](manifest) == expected
    assert API["content_hash"]({}) == hashlib.md5(b"[]").hexdigest()
    assert API["content_hash"]({"config": {"platform": None}}) == API["content_hash"]({})
    assert API["content_hash"]({"config": {"platform": {}}}) != API["content_hash"]({})
    manifest["description"] = "Ignored by Composer content hash"
    manifest["scripts"] = {}
    assert API["content_hash"](manifest) == expected
    manifest["require"] = {"vendor/a": "^1", "vendor/b": "^2"}
    assert API["content_hash"](manifest) != expected, "Nested order must be preserved"
    for key in API["CONTENT_KEYS"]:
        assert API["content_hash"]({key: "changed"}) != API["content_hash"]({})
    print("PASS content hash: Composer keys, outer-only sorting, PHP empty/numeric objects, Unicode, slashes, floats")


def inventory_checks():
    with tempfile.TemporaryDirectory(prefix=".inventory-fixture-", dir=ROOT / "scripts") as directory:
        root = Path(directory)
        manifest = {"require": {"php": "^7.1.3", "laravel/framework": "5.8.*", "vendor/missing": "^1.0", "vendor/direct": "^1.0"},
                    "require-dev": {"vendor/dev-only": "^1.0"}, "config": {"platform": {"php": "7.4.33", "ext-redis": False}},
                    "scripts": {"post-install-cmd": "touch NEVER_EXECUTE"}}
        (root / "composer.json").write_text(json.dumps(manifest))
        lock = {"content-hash": API["content_hash"](manifest), "packages": [
            {"name": "laravel/framework", "version": "v5.8.38", "require": {"php": "^7.1.3"},
             "source": {"url": "https://PRIVATE_SENTINEL:SECRET_SENTINEL@example.test/repo"}},
            {"name": "vendor/direct", "version": "1.0.0"},
            {"name": "vendor/plain", "version": "1.0.0"},
            {"name": "vendor/another-plain", "version": "1.0.0"},
            {"name": "vendor/abandoned", "version": "1.0.0", "abandoned": True},
            {"name": "vendor/capped", "version": "1.0.0", "require": {
                "illuminate/support": "^8.0", "laravel/framework": "^8.0",
                "illuminate/contracts": "^8.0", "illuminate/events": "^7.0 || ^8.0", "php": "^7.4"},
             "require-dev": {"illuminate/testing": "^99.0"}}],
            "packages-dev": [{"name": "vendor/dev-only", "version": "1.0.0"}]}
        (root / "composer.lock").write_text(json.dumps(lock))
        (root / "package.json").write_text(json.dumps({"dependencies": {"private-package": "https://SECRET_SENTINEL@example.test"}}))
        (root / ".env").write_text("PRIVATE_SENTINEL=SECRET_SENTINEL")
        for folder in ("app", "config", "bootstrap/cache", "docker/app", ".github/workflows",
                       "docker/too/deep", "Modules/Feature", "packages/feature", "modules/other"):
            (root / folder).mkdir(parents=True, exist_ok=True)
        (root / "app/Model.php").write_text("<?php\nprotected $dates = []; // SECRET_SENTINEL\nenv('PRIVATE_SENTINEL');\n")
        (root / "config/app.php").write_text("<?php env('APP_NAME');")
        (root / "bootstrap/cache/config.php").write_text("<?php serialize($generated); $dates = [];")
        (root / "Modules/Feature/Model.php").write_text("<?php $dates = [];")
        (root / "modules/other/Model.php").write_text("<?php $dates = [];")
        (root / "packages/feature/Model.php").write_text("<?php $dates = [];")
        (root / "docker/app/Dockerfile").write_text("ARG SECRET_SENTINEL\nFROM php:8.3-fpm\nRUN NEVER_EXECUTE\n")
        (root / "docker/too/deep/Dockerfile").write_text("FROM SHOULD_NOT_APPEAR")
        (root / ".github/workflows/tests.yml").write_text("SECRET_SENTINEL")
        (root / ".github/workflows/composer.json").write_text("SECRET_SENTINEL")
        (root / ".gitlab-ci.yml").write_text("SECRET_SENTINEL")
        (root / "bitbucket-pipelines.yml").write_text("SECRET_SENTINEL")
        (root / "deploy.php").write_text("<?php NEVER_EXECUTE();")
        (root / "Envoy.blade.php").write_text("NEVER_EXECUTE")
        compose_files = ("compose.yaml", "compose.yml", "compose.override.yaml", "compose.test.local.yml",
                         "docker-compose.yml", "docker-compose.override.yaml")
        for name in compose_files + ("compose.json", "composer.yaml", "docker-compose.yaml.bak"):
            (root / name).write_text("SECRET_SENTINEL")
        before = {p.relative_to(root): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in root.rglob("*") if p.is_file()}
        report = API["inventory"](root, "13", True)
        assert report["framework_locked"] == "v5.8.38"
        assert report["framework_constraint"] == "5.8.*"
        assert report["hop_path"] == ["5.8"] + [str(n) for n in range(6, 14)]
        assert report["production_parity"] == "unverified"
        assert report["platform"]["ext-redis"] is False
        assert report["lock_in_sync"] is True
        assert report["lock_content_hash"] == report["computed_content_hash"]
        assert report["root_requirements_without_named_lock_entry"] == ["vendor/missing"]
        packages = {package["name"]: package for package in report["locked_packages"]}
        assert len(packages) == 7 and "package_summary" not in report  # Full output remains the default.
        assert packages["vendor/capped"]["framework_requirements"] == {
            "^8.0": ["illuminate/contracts", "illuminate/support", "laravel/framework"],
            "^7.0 || ^8.0": ["illuminate/events"]}
        assert packages["vendor/plain"]["framework_requirements"] == {}
        brief = API["inventory"](root, "13", True, brief=True)
        assert {package["name"] for package in brief["locked_packages"]} == {
            "laravel/framework", "vendor/direct", "vendor/dev-only", "vendor/abandoned", "vendor/capped"}
        assert brief["package_summary"] == {"output": "brief", "total_locked": 7, "reported_locked": 5, "omitted_locked": 2}
        assert brief["root_requirements_without_named_lock_entry"] == report["root_requirements_without_named_lock_entry"]
        assert brief["source_scan"] == report["source_scan"]
        cli = subprocess.run([sys.executable, "-I", str(ROOT / "scripts/inventory.py"), str(root),
                              "--scan", "--target", "13", "--brief"], text=True, capture_output=True, check=True)
        assert json.loads(cli.stdout) == brief
        assert len(cli.stdout.encode()) < len(json.dumps(report, indent=2, ensure_ascii=False).encode())
        hints = report["source_scan"]["hints"]
        assert "app/Model.php:2" in hints["model_dates"]["examples"]
        assert hints["model_dates"]["matched_lines"] == 4  # app + Modules + modules + packages
        assert hints["serialization"]["matched_lines"] == 0  # generated bootstrap/cache excluded
        assert hints["env_outside_config"]["matched_lines"] == 1
        assert "loose_comparison" not in hints
        runtime = report["runtime_files_to_review"]
        for expected in ("docker/app/Dockerfile (FROM php:8.3-fpm)", ".github/workflows/tests.yml",
                         ".gitlab-ci.yml", "bitbucket-pipelines.yml", "deploy.php", "Envoy.blade.php"):
            assert expected in runtime, expected
        assert all(name in runtime for name in compose_files)
        assert not any(name in runtime for name in ("composer.json", "composer.lock", ".github/workflows/composer.json",
                                                    "compose.json", "composer.yaml", "docker-compose.yaml.bak"))
        assert not any("SHOULD_NOT_APPEAR" in line or "RUN " in line or "ARG " in line for line in runtime)
        assert "SECRET_SENTINEL" not in json.dumps(report) and "PRIVATE_SENTINEL" not in json.dumps(report)
        after = {p.relative_to(root): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in root.rglob("*") if p.is_file()}
        assert before == after and not (root / "NEVER_EXECUTE").exists()
        manifest["require"]["vendor/missing"] = "^2.0"
        (root / "composer.json").write_text(json.dumps(manifest))
        assert API["inventory"](root)["lock_in_sync"] is False
        lock.pop("content-hash")
        (root / "composer.lock").write_text(json.dumps(lock))
        assert API["inventory"](root)["lock_in_sync"] is None
        (root / "composer.lock").unlink()
        assert API["inventory"](root)["lock_in_sync"] is None
        assert API["inventory"](root)["hop_path"] is None
        assert API["hop_path"]("dev-main", "13") is None
        assert API["hop_path"]("v5.0.0", "13") == HOPS
        assert API["hop_path"]("v13.38.0", "13") == ["13"]
        try:
            API["hop_path"]("v13.38.0", "12")
        except ValueError:
            pass
        else:
            raise AssertionError("Downgrade was not rejected")
        (root / "composer.lock").symlink_to(root / "composer.json")
        try:
            API["inventory"](root)
        except ValueError:
            pass
        else:
            raise AssertionError("Symlinked metadata was accepted")
        (root / "composer.lock").unlink()
        (root / "resources").symlink_to(root / "app", target_is_directory=True)
        assert any("symlinked" in w for w in API["scan"](root)["warnings"])
        (root / "composer.json").write_text("not json")
        try:
            API["inventory"](root)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid metadata was accepted")
    print("PASS inventory: lock hashes, grouped raw framework requirements, full/brief CLI filters, runtime discovery and no writes")


def pattern_checks():
    patterns = API["compiled_patterns"]("v8.83.29", ())
    assert len(API["HELPERS"]) == 42 and len(set(API["HELPERS"])) == 42
    for helper in API["HELPERS"]:
        label = "php85_array_helpers" if helper in {"array_first", "array_last"} else "legacy_helpers"
        expected = helper != "str_contains"
        assert bool(patterns[label].search(helper + "($value);")) is expected, helper
        assert not patterns[label].search("$object->" + helper + "($value);"), helper
    assert API["compiled_patterns"]("v5.8.38")["legacy_helpers"].search("str_contains($a, $b)")
    assert API["compiled_patterns"]("v6.20.0", {"laravel/helpers"})["legacy_helpers"].search("str_contains($a, $b)")
    assert not API["compiled_patterns"]("v6.20.0")["legacy_helpers"].search("str_contains($a, $b)")
    assert patterns["upsert_unique_by"].search("$query->upsert($rows, [], ['name']);")
    assert patterns["upsert_unique_by"].search("Flight::upsert($rows, ['code'], ['name']);")
    cases = {
        "legacy_helpers": ("array_get($data, 'key');", "str_contains($text, 'native'); $obj->array_get();"),
        "php85_array_helpers": ("array_first($data, $callback); array_last($data);", "Arr::first($data); $obj->array_last();"),
        "serialization": ("serialize($value); unserialize($value); function serializeDate($date) {}", "$(this).serialize(); $obj->serialize(); Type::serialize();"),
        "upsert_unique_by": ("Flight::upsert($rows, ['code'], ['name']);", "$query->update($rows); Flight::update($rows); upsert($rows);"),
        "csrf_middleware_exclusions": ("->withoutMiddleware([\n VerifyCsrfToken::class,\n ValidateCsrfToken::class\n]);", "->withoutMiddleware([Authenticate::class]); VerifyCsrfToken::class;"),
        "exception_handler_signatures": ("public function render($request, \\Exception $e) {}", "public function render($request, \\Throwable $e) {}"),
        "blade_or_default": ("{{ $title or 'Default' }}", "{{ $title ?? 'Default' }} {{ $flag || $other }}"),
        "cache_integer_ttl": ("Cache::put('a', $value, 60); Cache::add('b', true, 10); Cache::remember('c', 30, $callback);", "Cache::put('a', 60, $expiry); Cache::remember('b', $ttl, $callback); Cache::put('x', get('y', 30), now());"),
    }
    for label, (positive, negative) in cases.items():
        pattern = API["compiled_patterns"]("v5.6.40")[label] if label == "blade_or_default" else patterns[label]
        assert pattern.search(positive), label + " missed its positive fixture"
        assert not pattern.search(negative), label + " matched its negative fixture"
    with tempfile.TemporaryDirectory(prefix=".pattern-fixture-", dir=ROOT / "scripts") as directory:
        root = Path(directory)
        (root / "app").mkdir()
        (root / "resources/views").mkdir(parents=True)
        for label, (positive, negative) in cases.items():
            target = root / ("app/Handler.php" if label == "exception_handler_signatures" else
                             "resources/views/probe.blade.php" if label == "blade_or_default" else "app/Probe.php")
            framework = "v5.6.40" if label == "blade_or_default" else "v8.83.29"
            target.write_text(positive)
            assert API["scan"](root, framework)["hints"][label]["matched_lines"] > 0, label
            target.write_text(negative)
            assert API["scan"](root, framework)["hints"][label]["matched_lines"] == 0, label
            target.unlink()
        blade = root / "resources/views/probe.blade.php"
        blade.write_text("{{-- {{ $hidden or 'x' }} --}}\n{{--\n{{ $alsoHidden or 'y' }}\n--}}\n\n{{ $visible or 'z' }}\n")
        result = API["scan"](root, "v5.6.40")["hints"]["blade_or_default"]
        assert result["matched_lines"] == 1 and result["examples"] == ["resources/views/probe.blade.php:6"]
        for framework in (None, "v5.7.0", "v5.8.38", "v8.83.29", "v13.38.0"):
            assert API["scan"](root, framework)["hints"]["blade_or_default"]["matched_lines"] == 0
        blade.write_text("{{-- unclosed comment\n{{ $hidden or 'x' }}\n")
        assert API["scan"](root, "v5.6.40")["hints"]["blade_or_default"]["matched_lines"] == 0
    print("PASS patterns: helpers, jQuery exclusion, guide hints, full Blade comment masking/line numbers and <5.7 gating")


def junit_checks():
    def xml(cases):
        return '<testsuites><testsuite name="suite">' + cases + '</testsuite></testsuites>'
    passed = '<testcase classname="Feature.Login" name="testLogin" assertions="2"/>'
    skipped = '<testcase classname="Feature.Login" name="testDenied" assertions="0"><skipped/></testcase>'
    legacy = passed.replace('classname="Feature.Login"', 'class="Feature' + chr(92) + 'Login"')
    warned = passed.replace('/>', '><warning>warning text</warning></testcase>')
    with tempfile.TemporaryDirectory(prefix=".junit-fixture-", dir=ROOT / "scripts") as directory:
        left, right = Path(directory) / "left.xml", Path(directory) / "right.xml"
        left.write_text(xml(passed + skipped))
        fixtures = [
            (xml(passed + skipped), 0, "MATCHES"),
            (xml(legacy + skipped), 0, "MATCHES"),
            (xml(warned + skipped), 1, "warning"),
            (xml(legacy + passed), 2, "Duplicate"),
            (xml(passed.replace('assertions="2"', 'assertions="9"') + skipped), 0, "INFO"),
            (xml(passed), 1, "missing from right"),
            (xml(passed + skipped + '<testcase classname="Other" name="extra"/>'), 1, "extra in right"),
            (xml(passed.replace('/>', '><failure>failed</failure></testcase>') + skipped), 1, "DIFF"),
            (xml(passed + skipped.replace('<skipped/>', '<error/>')), 1, "DIFF"),
            (xml(passed + passed), 2, "Duplicate"),
            ("<testsuites/>", 2, "no testcases"),
            ("", 2, "Unusable"),
            ("<testsuites>", 2, "Unusable"),
            ('<!DOCTYPE x [<!ENTITY xx SYSTEM "file:///NEVER_READ">]><testsuite/>', 2, "DTD"),
            ('<!DOCTYPE x [<!ENTITY xx "never expand">]><testsuite/>'.encode("utf-16"), 2, "DTD"),
        ]
        for content, expected, message in fixtures:
            right.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
            result = subprocess.run([sys.executable, "-I", str(ROOT / "scripts/compare_junit.py"), str(left), str(right)],
                                    text=True, capture_output=True)
            assert result.returncode == expected, (expected, result.returncode, result.stderr)
            assert message in result.stdout + result.stderr, message
        left.write_text(xml(warned + skipped))
        right.write_text(xml(passed + skipped))
        assert JUNIT["compare"](left, right)[0] == 1
        for children, expected in (("<error/><failure/><warning/><skipped/>", "error"),
                                   ("<failure/><warning/><skipped/>", "fail"),
                                   ("<warning/><skipped/>", "warning")):
            right.write_text(xml(passed.replace('/>', '>' + children + '</testcase>')))
            assert JUNIT["load_report"](right)["Feature.Login::testLogin"]["status"] == expected
        right.write_text('<testsuite xmlns="urn:junit">' + passed + '</testsuite>')
        assert len(JUNIT["load_report"](right)) == 1
    print("PASS JUnit CLI: legacy class normalization, warning precedence/both directions, 0/1/2 exits, assertions, XML safety")


def plan_history_checks():
    with tempfile.TemporaryDirectory(prefix=".plan-fixture-", dir=ROOT / "scripts") as directory:
        root = Path(directory).resolve()
        repo, workspace, notes = root / "repository", root / "worktree", root / "private-notes"
        repo.mkdir()
        notes.mkdir()
        archives = workspace / "docs/upgrade/plans"
        archives.mkdir(parents=True)
        active = workspace / "docs/upgrade/plan.md"
        state_path = workspace / "docs/upgrade/run-state.json"
        source1, copy1 = notes / "plan-2026-10-26.md", archives / "plan-v1.md"
        source1.write_text("Approved original plan.\n")
        original = source1.read_bytes()
        sha1 = hashlib.sha256(original).hexdigest()
        copy1.write_bytes(original)
        active.write_bytes(original)
        invoked_at = "2026-10-26T10:00:00Z"
        state = {
            "schema_version": 2, "project": {"root_path": str(repo)}, "workspace": {"path": str(workspace)},
            "approved_plan": {"version": 1, "source_path": str(source1), "path": "docs/upgrade/plan.md", "sha256": sha1},
            "plan_versions": [{"version": 1, "source_path": str(source1), "copy_path": "docs/upgrade/plans/plan-v1.md",
                               "sha256": sha1, "approved_at": invoked_at, "approval_ref": "approval-001"}],
            "approvals": {"range_invocation": {"id": "approval-001", "kind": "range-command", "invoked_at": invoked_at,
                          "command": f'/laravel-upgrade-step "{repo}" "5.8 -> 13" "{source1}"',
                          "plan_source_path": str(source1), "plan_sha256": sha1}, "decisions": []},
            "hop_attempts": {"5.8->6": {"rounds_used": 2, "max_rounds": 3}},
            "progress": {"closed_hops": [{"plan_version": 1, "plan_sha256": sha1}]},
        }
        def save():
            state_path.write_text(json.dumps(state))
        def blocked():
            try:
                validate_plan_history(state_path, source1)
            except ValueError:
                return
            raise AssertionError("Unapproved or inconsistent plan change was accepted")
        save()
        assert validate_plan_history(state_path, source1) == 1
        source1.write_bytes(original + b"unapproved edit")
        blocked()
        source1.write_bytes(original)
        active.write_bytes(b"unrecorded worktree edit")
        blocked()
        active.write_bytes(original)
        source2, copy2 = notes / "plan-2026-10-26-v2.md", archives / "plan-v2.md"
        source2.write_text("Approved revised plan: keep PHP session serialization.\n")
        revised = source2.read_bytes()
        sha2 = hashlib.sha256(revised).hexdigest()
        copy2.write_bytes(revised)
        active.write_bytes(revised)
        approved_at = "2026-10-26T11:00:00Z"
        decision = {"id": "approval-002", "kind": "user-decision", "approved_at": approved_at,
                    "user_response": "Keep PHP session serialization for this range.", "redactions": [], "plan_sha256": sha2}
        state["approvals"]["decisions"].append(decision)
        state["plan_versions"].append({"version": 2, "source_path": str(source2), "copy_path": "docs/upgrade/plans/plan-v2.md",
                                       "sha256": sha2, "approved_at": approved_at, "approval_ref": "approval-002"})
        state["approved_plan"] = {"version": 2, "source_path": str(source2), "path": "docs/upgrade/plan.md", "sha256": sha2}
        unrecorded_version = state["plan_versions"].pop()
        save()
        blocked()  # Updating the active pointer without appending history is not enough.
        state["plan_versions"].append(unrecorded_version)
        save()
        before_validation = state_path.read_bytes()
        assert validate_plan_history(state_path, source1) == 2  # Same old command follows latest approved version.
        assert validate_plan_history(state_path, source2) == 2
        assert state_path.read_bytes() == before_validation  # Read-only validation cannot reset counters.
        persisted = json.loads(before_validation)
        assert persisted["hop_attempts"]["5.8->6"]["rounds_used"] == 2
        assert persisted["progress"]["closed_hops"][0]["plan_sha256"] == sha1
        state["approvals"]["decisions"] = []
        save()
        blocked()
        state["approvals"]["decisions"] = [decision]
        save()
        command = [sys.executable, "-I", str(ROOT / "scripts/check.py"), "--run-state", str(state_path), "--plan-source", str(source1)]
        result = subprocess.run(command, text=True, capture_output=True)
        assert result.returncode == 0 and "version 2" in result.stdout, result.stderr
        source2.write_bytes(revised + b"unapproved further change")
        result = subprocess.run(command, text=True, capture_output=True)
        assert result.returncode == 2 and "BLOCKED" in result.stderr
        source2.write_bytes(revised)
        # Committed state may use home-relative paths (~/...) so a pushed branch does not reveal local usernames.
        saved_home = os.environ.get("HOME")
        os.environ["HOME"] = str(root)
        try:
            home = lambda value: "~/" + Path(value).relative_to(root).as_posix()
            state["project"]["root_path"], state["workspace"]["path"] = home(repo), home(workspace)
            for row in state["plan_versions"] + [state["approved_plan"]]:
                row["source_path"] = home(row["source_path"])
            invocation = state["approvals"]["range_invocation"]
            invocation["plan_source_path"] = home(invocation["plan_source_path"])
            save()
            assert validate_plan_history(state_path, home(source1)) == 2
        finally:
            if saved_home is None:
                os.environ.pop("HOME", None)
            else:
                os.environ["HOME"] = saved_home
        state["plan_versions"][-1]["source_path"] = "relative-plan.md"
        save()
        blocked()
    print("PASS plan history: durable source/copy hashes, approved v2 resume from original command, no counter reset, tamper/missing approval blocked")


def reference_checks():
    manifest = json.loads((ROOT / "references/source-manifest.json").read_text())
    records = manifest["files"]
    paths = [record["path"] for record in records]
    assert len(paths) == len(set(paths)), "Duplicate reference paths"
    versions = [f"5.{n}" for n in range(9)] + [f"{n}.x" for n in range(6, 14)]
    for version in versions:
        for filename in ("upgrade.md", "releases.md", "framework-composer.json"):
            assert f"official/{version}/{filename}" in paths, f"Missing {version}/{filename}"
    for record in records:
        path = (ROOT / "references" / record["path"]).resolve()
        assert path.is_relative_to(ROOT / "references/official"), "Reference escapes official directory"
        data = path.read_bytes()
        assert len(data) == record["bytes"]
        assert hashlib.sha256(data).hexdigest() == record["sha256"], f"Hash mismatch: {record['path']}"
        assert re.fullmatch(r"[a-f0-9]{40}", record["commit"])
        parsed = urlparse(record["url"])
        assert parsed.scheme == "https" and parsed.netloc == "raw.githubusercontent.com"
        assert parsed.path.startswith(f"/{record['repository']}/{record['commit']}/")
        assert record["repository"] in {"laravel/docs", "laravel/framework"}
    added = ROOT / "references/official/13.x/TransformsRequest-v13.38.0.php"
    assert "$maxKeyBytes = 20 * 1024 * 1024" in added.read_text()
    assert len(records) == 70, "Expected original 69 files plus one source snapshot"
    print(f"PASS local official sources: {len(records)} hashes and pinned URLs, {len(versions)} Laravel lines; no downloads")


def execution_contract_checks():
    core = (ROOT / "SKILL.md").read_text()
    step = (ROOT.parent / "laravel-upgrade-step/SKILL.md").read_text()
    readme = (ROOT / "README.md").read_text()
    templates = (ROOT / "references/templates.md").read_text()
    assert "Approved source: none (draft)" in templates
    assert "Plan version / SHA-256: N/A until approval" in templates
    blocks = [json.loads(block) for block in re.findall(r"```json\n(.*?)\n```", templates, re.S)]
    state = next(block for block in blocks if "schema_version" in block)
    assert state["schema_version"] == 2
    assert Path(state["approved_plan"]["source_path"]).expanduser().is_absolute()
    assert state["plan_versions"] and state["approvals"]["range_invocation"]["kind"] == "range-command"
    assert state["baseline"]["original"]["commit_sha"]
    assert "lock_content_hash" in state["baseline"]["original"]
    assert "computed_content_hash" in state["baseline"]["original"]
    assert state["baseline"]["reconciled"] is None
    assert state["workspace"]["branch"] == "upgrade/laravel-<x>-to-<y>"
    assert "current_hop" in state["progress"] and "next_hop" in state["progress"]
    assert all(row["max_rounds"] == 3 and row["rounds_used"] == 0 for row in state["hop_attempts"].values())
    assert state["retry_reset_history"] == []
    assert state["runtime_by_hop"] and state["approved_plan"]["sha256"]
    assert "print" in core and "/laravel-upgrade-step /absolute/app/path" in core
    for text in (core, readme):
        for line in text.splitlines():
            if line.startswith("/laravel-upgrade-step "):
                command = shlex.split(line)
                assert len(command) == 4 and Path(command[1]).is_absolute() and Path(command[3]).is_absolute()
    for text in (step, readme):
        for marker in ("run-state.json", "upgrade/laravel-<x>-to-<y>", "PARTIAL", "3", "reset", "worktree"):
            assert marker in text, marker
    assert "explicit user permission" in step and "intervention" in step
    assert "Level 0" in step and "Security regressions cannot be accepted" in step
    print("PASS execution contract: JSON run-state, immutable/reconciled B hashes, persistent 3-round budget, manual range entry/resume docs")


def skill_checks():
    skill_roots = [ROOT] + [ROOT.parent / f"laravel-upgrade-{suffix}" for suffix in ("audit", "step", "verify")]
    for skill in skill_roots:
        content = (skill / "SKILL.md").read_text()
        assert content.startswith("---\n")
        frontmatter = content.split("---", 2)[1]
        assert f"name: {skill.name}\n" in frontmatter
        assert "description:" in frontmatter and "argument-hint:" in frontmatter
        assert len(content.splitlines()) < 500
    step = (ROOT.parent / "laravel-upgrade-step/SKILL.md").read_text()
    assert "disable-model-invocation: true" in step
    assert "../laravel-upgrade-step/SKILL.md" not in (ROOT / "SKILL.md").read_text()
    files = [skill / "SKILL.md" for skill in skill_roots]
    files += list((ROOT / "references").glob("*.md")) + [ROOT / "README.md"]
    for file in files:
        text = file.read_text()
        # Extra private terms (client/project names) can be supplied locally: LARAVEL_UPGRADE_PRIVATE_TERMS="a,b".
        private_terms = ["project-snapshots.md"] + [t for t in os.environ.get("LARAVEL_UPGRADE_PRIVATE_TERMS", "").split(",") if t]
        for forbidden in private_terms:
            assert forbidden not in text, f"Private/stale project data in {file.name}: {forbidden}"
        assert not re.search(r"(?:/Users|/home|/Volumes)/[\w.-]+/", text), f"Absolute personal path in {file.name}"
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if target.startswith(("http:", "https:", "mailto:", "#")):
                continue
            relative = unquote(target.split("#", 1)[0])
            assert (file.parent / relative).exists(), f"Broken link in {file.name}: {target}"
    print(f"PASS skills: four frontmatters, manual execution guard, links/privacy in {len(files)} authored documents")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-state", help="Validate only the approved plan history in this absolute run-state path")
    parser.add_argument("--plan-source", help="Optional original/current absolute source path from the user's command")
    args = parser.parse_args()
    if args.plan_source and not args.run_state:
        parser.error("--plan-source requires --run-state")
    if args.run_state:
        try:
            version = validate_plan_history(args.run_state, args.plan_source)
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
            print(f"BLOCKED plan history: {error}", file=sys.stderr)
            sys.exit(2)
        print(f"PASS approved plan version {version}: source, archived copy and active copy hashes match")
    else:
        hash_checks()
        inventory_checks()
        pattern_checks()
        junit_checks()
        plan_history_checks()
        reference_checks()
        execution_contract_checks()
        skill_checks()
        print("All offline suite checks passed. No application runtime or network was used.")

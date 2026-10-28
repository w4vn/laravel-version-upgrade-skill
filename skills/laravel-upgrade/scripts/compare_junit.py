#!/usr/bin/env python3
"""Compare JUnit testcase identity/status; never load or boot an application."""
import argparse
from collections import Counter
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET


def load_report(path):
    with Path(path).open("rb") as stream:
        data = stream.read(32_000_001)
    if len(data) > 32_000_000:
        raise ValueError("JUnit report exceeds 32 MB limit")
    if re.search(br"<!\s*(?:DOCTYPE|ENTITY)\b", data.replace(b"\x00", b""), re.I):
        raise ValueError("DTD/entity declarations are not allowed in JUnit input")
    root = ET.fromstring(data)
    rows = {}
    for case in root.iter():
        if case.tag.rsplit("}", 1)[-1] != "testcase":
            continue
        classname = case.get("classname") or (case.get("class") or "").replace(chr(92), ".")
        name = case.get("name")
        if not classname or not name:
            raise ValueError("Every testcase needs a non-empty classname (or legacy class) and name")
        key = classname + "::" + name
        if key in rows:
            raise ValueError(f"Duplicate testcase: {key}")
        children = {child.tag.rsplit("}", 1)[-1] for child in case}
        status = next((kind for tag, kind in (("error", "error"), ("failure", "fail"),
                                               ("warning", "warning"), ("skipped", "skipped"))
                       if tag in children), "pass")
        assertions = case.get("assertions")
        if assertions is not None:
            if not re.fullmatch(r"[0-9]+", assertions):
                raise ValueError(f"Invalid assertion count: {key}")
            assertions = int(assertions)
        rows[key] = {"status": status, "assertions": assertions}
    if not rows:
        raise ValueError("JUnit report contains no testcases")
    return rows


def compare(left, right):
    a, b = load_report(left), load_report(right)
    lines, different = [], False
    for key in sorted(a.keys() | b.keys()):
        if key not in a or key not in b:
            lines.append(f"DIFF {key}: {'extra in right' if key not in a else 'missing from right'}")
            different = True
        elif a[key]["status"] != b[key]["status"]:
            lines.append(f"DIFF {key}: {a[key]['status']} -> {b[key]['status']}")
            different = True
        if key in a and key in b and a[key]["assertions"] != b[key]["assertions"]:
            lines.append(f"INFO {key}: assertions {a[key]['assertions']} -> {b[key]['assertions']}")
    lines.extend(f"{label}: {len(rows)} testcases {dict(sorted(Counter(row['status'] for row in rows.values()).items()))}"
                 for label, rows in (("left", a), ("right", b)))
    lines.append("DIFFERENT" if different else "MATCHES (parity, not necessarily an all-green suite)")
    lines.append("Also retain PHPUnit exit codes and CLI warnings/risky/deprecation/incomplete details; JUnit may omit them.")
    return (1 if different else 0), lines


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left", help="Baseline or previous-hop JUnit XML")
    parser.add_argument("right", help="Candidate JUnit XML")
    args = parser.parse_args(argv)
    try:
        result, lines = compare(args.left, args.right)
    except (OSError, ValueError, ET.ParseError) as error:
        print(f"Unusable JUnit report: {error}", file=sys.stderr)
        return 2
    print("\n".join(lines))
    return result


if __name__ == "__main__":
    sys.exit(main())

"""Verify relocation preservation, syntax, and local-link regressions offline."""

import ast
import hashlib
import json
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt

from relocation_support import HERE, ROOT, historical_bytes, repo_path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def descendants(tokens):
    for token in tokens:
        yield token
        yield from descendants(token.children or [])


def main():
    manifest = json.loads((HERE / "manifest.json").read_text())
    records = manifest["files"]
    errors = []
    parser = MarkdownIt("commonmark").enable("table")
    archive = HERE / "originals.zip"
    if sha(archive) != manifest["originals_archive_sha256"]:
        errors.append("Originals archive hash changed")
    archived_count = 0
    with zipfile.ZipFile(archive) as original:
        for record in records:
            path = ROOT / record["new_path"]
            if not path.is_file() or sha(path) != record["after_sha256"]:
                errors.append("Missing or changed relocated file: " + record["new_path"])
                continue
            if record["before_sha256"] != record["after_sha256"]:
                data = original.read(record["old_path"])
                archived_count += 1
                if hashlib.sha256(data).hexdigest() != record["before_sha256"]:
                    errors.append("Original bytes lost: " + record["old_path"])
            if path.suffix == ".py":
                ast.parse(path.read_text(), filename=record["new_path"])
    for record in manifest["unaffected_original_files"]:
        path = ROOT / record["path"]
        if not path.is_file() or sha(path) != record["sha256"]:
            errors.append("Unrelated file changed: " + record["path"])
    if (ROOT / manifest["source"]).exists():
        errors.append("The old top-level package still exists")
    retained = [r for r in records if r["old_path"].startswith("ai-system-design/")]
    if len(retained) != manifest["original_package_files"]:
        errors.append("Original file inventory count changed")

    def local_links(text, path):
        for token in descendants(parser.parse(text)):
            value = token.attrGet("href") if token.type == "link_open" else token.attrGet("src") if token.type == "image" else None
            if not value:
                continue
            parts = urlsplit(value)
            if parts.scheme or parts.netloc or not parts.path:
                continue
            yield value, (path.parent / unquote(parts.path)).resolve()

    checked, preexisting, regressions = 0, [], []
    originals = [{"old_path": r["path"], "new_path": r["path"]} for r in manifest["unaffected_original_files"]]
    for record in records + originals:
        path = ROOT / record["new_path"]
        if path.suffix != ".md":
            continue
        old_missing = set()
        for _, dest in local_links(historical_bytes(path).decode(), ROOT / record["old_path"]):
            if dest.is_relative_to(ROOT):
                dest = repo_path(dest.relative_to(ROOT))
            if not dest.exists():
                old_missing.add(str(dest))
        for target, dest in local_links(path.read_text(), path):
            checked += 1
            if not dest.exists():
                row = {"file": record["new_path"], "target": target}
                (preexisting if str(dest) in old_missing else regressions).append(row)
    for path in (ROOT / "eval/README.md", HERE / "README.md"):
        for target, dest in local_links(path.read_text(), path):
            checked += 1
            if not dest.exists() and dest != HERE / "verification.json":
                regressions.append({"file": str(path.relative_to(ROOT)), "target": target})
    errors.extend("Introduced broken link: " + json.dumps(row) for row in regressions)
    result = {
        "status": "FAIL" if errors else "PASS",
        "verified_at_utc": datetime.now(UTC).isoformat(),
        "original_package_files_retained": len(retained),
        "unchanged_package_files": sum(r["before_sha256"] == r["after_sha256"] for r in retained),
        "edited_originals_preserved_in_archive": archived_count,
        "unchanged_files_outside_package": len(manifest["unaffected_original_files"]),
        "local_links_checked": checked,
        "introduced_broken_links": regressions,
        "preexisting_missing_local_targets": preexisting,
        "errors": errors,
        "new_model_calls": 0,
        "scope": "File hashes, archived original bytes, Python syntax, and local link regressions. Separate receipts verify frozen evaluation and ground-truth evidence.",
    }
    (HERE / "verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())

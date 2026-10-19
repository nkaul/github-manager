"""Read-only checks of article data, links, images and preserved source evidence."""

import ast
import hashlib
import json
import sys
import math
import re
import struct
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
sys.path.insert(0, str(ROOT / "eval/relocation"))
from relocation_support import historical_bytes, historical_sha256, repo_path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def descendants(tokens):
    for token in tokens:
        yield token
        yield from descendants(token.children or [])


def slug(text):
    return re.sub(r"[^\w\- ]", "", text.lower()).replace(" ", "-")


def main():
    errors = []
    parser = MarkdownIt("commonmark").enable("table")
    markdowns = sorted(BASE.rglob("*.md"))
    links = external = 0
    for path in markdowns:
        source = path.read_text()
        tokens = parser.parse(source)
        for token in descendants(tokens):
            target = token.attrGet("href") if token.type == "link_open" else token.attrGet("src") if token.type == "image" else None
            if not target:
                continue
            links += 1
            parts = urlsplit(target)
            if parts.scheme:
                external += 1
                if parts.scheme != "https":
                    errors.append(f"Unexpected external scheme in {path.name}")
                continue
            dest = (path.parent / unquote(parts.path)).resolve() if parts.path else path
            if not dest.is_file():
                if dest == BASE / "verification.json":
                    continue  # This run creates the linked verification output below.
                errors.append(f"Missing relative target {path.name}: {target}")
                continue
            fragment = unquote(parts.fragment)
            if fragment.startswith("L") and fragment[1:].isdigit():
                if int(fragment[1:]) > len(dest.read_text().splitlines()):
                    errors.append(f"Bad source line {target}")
            elif fragment and dest.suffix == ".md":
                headers = re.findall(r"^#{1,6} (.+)$", dest.read_text(), re.M)
                if fragment not in {slug(h) for h in headers}:
                    errors.append(f"Missing heading {target}")
        if source.count("```") % 2:
            errors.append(f"Unclosed fenced block {path.name}")
    manifest = json.loads((BASE / "source-manifest.json").read_text())
    for path, digest in manifest["sha256"].items():
        if historical_sha256(repo_path(path)) != digest:
            errors.append(f"Changed original source/report: {path}")
    data = json.loads((BASE / "measurements.json").read_text())
    for record in data["sources"].values():
        if sha(ROOT / record["path"]) != record["sha256"]:
            errors.append("Frozen experiment source changed")
    r = data["round2"]
    checks = [
        r["metrics"]["ALL"]["tp"] == 50, r["metrics"]["ALL"]["fp"] == 0,
        r["metrics"]["ALL"]["fn"] == 2, r["input_tokens"] == 16041,
        r["output_tokens"] == 3414, r["reasoning_tokens_in_output"] == 702,
        r["count_http_200"] == r["generation_http_200"] == 20,
        math.isclose(r["metrics"]["ALL"]["f1"], 100 / 102),
        math.isclose(r["ledger_rounded_usd"], 0.003319),
        math.isclose(r["raw_token_rate_usd"], 0.0033111),
        math.isclose(r["input_plus_output_per_true_positive"], 389.1),
    ]
    if not all(checks):
        errors.append("Headline arithmetic mismatch")
    images = sorted((BASE / "figures").glob("*.png"))
    svgs = sorted((BASE / "figures").glob("*.svg"))
    if len(images) != 8 or len(svgs) != 8:
        errors.append("Expected exactly eight PNG and SVG figure pairs")
    for path in images:
        header = path.read_bytes()[:24]
        if header[:8] != b"\x89PNG\r\n\x1a\n" or struct.unpack(">II", header[16:24]) != (3600, 2160):
            errors.append(f"PNG dimension/format error {path.name}")
    for path in svgs:
        ET.parse(path)
    layout = json.loads((BASE / "figures/layout-audit.json").read_text())
    if layout["status"] != "PASS" or len(layout["figures"]) != 8 or any(x["failures"] for x in layout["figures"]):
        errors.append("Figure layout audit did not pass")
    article = (BASE / "github-manager-ai-system-design.md").read_text()
    chapters = re.findall(r"^## (\d+)\.", article, re.M)
    if chapters != [str(i) for i in range(1, 21)]:
        errors.append("Article chapter ordering")
    if len(re.findall(r"^\*Figure \d+\.", article, re.M)) != 8:
        errors.append("Expected eight article captions")
    if len(re.findall(r"^!\[", article, re.M)) != 8:
        errors.append("Expected eight article figures")
    illustrated = BASE / "illustrated"
    illustrated_dimensions = {}
    preserved_academic = 0
    if illustrated.is_dir():
        preservation = json.loads((illustrated / "academic-preservation.json").read_text())
        for name, digest in preservation["sha256"].items():
            if historical_sha256(BASE / name) != digest:
                errors.append(f"Academic edition changed: {name}")
            preserved_academic += 1
        illustrated_images = sorted((illustrated / "figures").glob("*.png"))
        if len(illustrated_images) != 8:
            errors.append("Expected eight separate illustrated figures")
        for image in illustrated_images:
            header = image.read_bytes()[:24]
            size = struct.unpack(">II", header[16:24])
            illustrated_dimensions[image.name] = list(size)
            if header[:8] != b"\x89PNG\r\n\x1a\n" or size[0] < 1500 or size[1] < 900:
                errors.append(f"Illustrated PNG dimension/format error {image.name}")
        review_path = illustrated / "figures/review.json"
        if not review_path.is_file():
            errors.append("Illustration review is missing")
        else:
            review = json.loads(review_path.read_text())
            if review.get("status") != "PASS" or len(review.get("figures", [])) != 8:
                errors.append("Illustration review is incomplete")
            for record in review.get("figures", []):
                if sha(illustrated / "figures" / record["file"]) != record["sha256"]:
                    errors.append(f"Illustration changed after review: {record['file']}")
        illustrated_article = (illustrated / "github-manager-ai-system-design-illustrated.md").read_text()
        if re.findall(r"^## (\d+)\.", illustrated_article, re.M) != chapters:
            errors.append("Illustrated edition must retain all academic chapters")
        if len(re.findall(r"^!\[", illustrated_article, re.M)) != 8:
            errors.append("Illustrated article must include all eight figures")
    for path in BASE.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix in {".sqlite", ".sqlite3", ".db"} or path.name == ".env" or path.name.endswith(".local.json"):
            errors.append(f"Raw state must not be in publication package: {path.name}")
        if path.suffix in {".md", ".json", ".py", ".cjs", ".svg"}:
            value = path.read_text()
            if re.search(r"gh[pousr]_[A-Za-z0-9]{24,}|\bAKIA[A-Z0-9]{16}\b|\bsk-[A-Za-z0-9_-]{24,}|/Users/[a-zA-Z0-9_-]+/", value):
                errors.append(f"Potential credential/absolute personal path: {path.name}")
        if path.suffix == ".py":
            ast.parse(path.read_text())
    changed = subprocess.check_output(["git", "diff", "--name-only", "HEAD"], cwd=ROOT, text=True).splitlines()
    unexpected = [p for p in changed if not p.startswith("eval/ai-system-design/")]
    if unexpected:
        errors.append("Tracked modifications outside article folder")
    output = {"status": "FAIL" if errors else "PASS", "audit_date": "2026-10-14",
              "article_words_whitespace_count": len(article.split()), "article_chapters": len(chapters),
              "markdown_files": len(markdowns), "links_checked": links, "external_https_links_syntax_only": external,
              "png_figures": len(images), "svg_figures": len(svgs), "png_dimensions": [3600, 2160],
              "preserved_source_report_files": len(manifest["sha256"]), "preserved_frozen_experiment_files": 2,
              "headline_numeric_checks": len(checks), "obvious_secret_scan": "PASS" if not any("credential" in e for e in errors) else "FAIL",
              "tracked_changes_outside_package": unexpected, "application_provider_calls": 0,
              "illustrated_figures_dimensions": illustrated_dimensions,
              "preserved_academic_article_and_diagrams": preserved_academic,
              "illustration_generation": "Built-in Image Generation tool; separate from application inference ledger",
              "errors": errors,
              "limits": "External references manually researched; this check does not test remote link availability, prove absence of every secret, rerun application tests or rerun provider generations."}
    (BASE / "verification.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

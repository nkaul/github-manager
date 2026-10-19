"""Resolve historical package paths without rewriting frozen evaluation evidence.

The archive is used only for a file whose *current* bytes match its recorded
post-relocation hash. A later edit therefore cannot silently pass an old check.
"""

import hashlib
import json
import zipfile
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def repo_path(name):
    """Translate a repository-relative name from a historical path manifest."""
    name = str(name)
    if name == "ai-system-design" or name.startswith("ai-system-design/"):
        name = "eval/" + name
    return ROOT / name


@lru_cache(maxsize=1)
def _records():
    manifest = json.loads((HERE / "manifest.json").read_text())
    return {row["new_path"]: row for row in manifest["files"]}


def historical_bytes(path):
    """Read proven original bytes for a relocation-only edit, else current bytes."""
    path = Path(path)
    data = path.read_bytes()
    try:
        name = path.relative_to(ROOT).as_posix()
    except ValueError:
        return data
    record = _records().get(name)
    if record and record["before_sha256"] != record["after_sha256"]:
        if hashlib.sha256(data).hexdigest() != record["after_sha256"]:
            raise ValueError("File changed after relocation: " + name)
        with zipfile.ZipFile(HERE / "originals.zip") as archive:
            original = archive.read(record["old_path"])
        if hashlib.sha256(original).hexdigest() != record["before_sha256"]:
            raise ValueError("Relocation archive mismatch: " + name)
        return original
    return data


def historical_sha256(path):
    """Hash original evidence bytes; ordinary content hashes stay separate."""
    return hashlib.sha256(historical_bytes(path)).hexdigest()

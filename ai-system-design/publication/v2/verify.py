"""Verify the v2 documentation package without services or live state writes."""

import hashlib
import json
import math
import os
import re
import struct
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SKILL = ROOT / ".agents/skills/engaging-technical-writing"
sys.path.insert(0, str(ROOT / "backend"))

from app.pretest.ai.chains import CLASSIFY_SYSTEM, TAXONOMY_SYSTEM  # noqa: E402
from app.pretest.ai.evidence import Retriever  # noqa: E402
from app.pretest.ai.schemas import Classification, TaxonomyDraft, validate_classification, validate_taxonomy  # noqa: E402
from app.pretest.ai.storage import digest  # noqa: E402


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def slug(text):
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"\s", "-", text)


def no_gold(value):
    if isinstance(value, dict):
        assert not {"gold", "labels", "expected_labels_for_evaluation_only"} & set(value)
        for v in value.values():
            no_gold(v)
    elif isinstance(value, list):
        for v in value:
            no_gold(v)


def model_user_payload(request):
    messages = [item for item in request["input"] if item["role"] == "user"]
    assert len(messages) == 1
    content = messages[0]["content"]
    text = content if isinstance(content, str) else "".join(item["text"] for item in content)
    return json.loads(text)


def main():
    failures = []
    baseline = load(HERE / "prior-artifacts-preservation.json")
    unchanged, navigation = [], []
    for name, expected in baseline["prior_article_files"].items():
        path = ROOT / name
        if name in baseline["navigation_original_bytes"]:
            original = path.read_bytes()[:baseline["navigation_original_bytes"][name]]
            assert hashlib.sha256(original).hexdigest() == expected, name
            navigation.append(name)
        else:
            assert sha(path) == expected, name
            unchanged.append(name)
    records = {str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/"docs/validation").rglob("*")) if p.is_file() and p.suffix in {".md", ".json"}}
    assert len(records) == baseline["validation_records_count"]
    assert hashlib.sha256(json.dumps(records,sort_keys=True).encode()).hexdigest() == baseline["validation_tree_sha256"]
    manifest = load(ROOT/"ai-system-design/source-manifest.json")
    for name, expected in manifest["sha256"].items():
        assert sha(ROOT/name) == expected, name

    md_files = sorted(HERE.rglob("*.md")) + sorted(SKILL.rglob("*.md"))
    checked, external = 0, set()
    for path in md_files:
        text = path.read_text()
        if len(re.findall(r"^```", text, re.M)) % 2:
            failures.append({"file":str(path.relative_to(ROOT)),"error":"Unclosed fenced code block"})
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                assert target.startswith("https://"), target
                external.add(target)
                continue
            destination, _, fragment = target.partition("#")
            resolved = (path.parent/unquote(destination)).resolve() if destination else path
            checked += 1
            # This command creates its own report after checking the package.
            if not resolved.exists() and resolved != HERE/"verification.json":
                failures.append({"file":str(path.relative_to(ROOT)),"target":target,"error":"Missing local target"})
            elif resolved.exists() and fragment and resolved.suffix == ".md":
                headings = {slug(h) for h in re.findall(r"^#{1,6}\s+(.+)$",resolved.read_text(),re.M)}
                if unquote(fragment) not in headings:
                    failures.append({"file":str(path.relative_to(ROOT)),"target":target,"error":"Missing heading"})

    secret_patterns = [r"\bgh[pousr]_[A-Za-z0-9]{20,}", r"\bsk-(?:proj-)?[A-Za-z0-9_-]{24,}", r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"]
    scanned = []
    for path in sorted(HERE.rglob("*")) + sorted(SKILL.rglob("*")):
        if not path.is_file() or path.suffix not in {".md", ".json", ".py", ".yaml", ".txt"} or path.name == "verification.json":
            continue
        text = path.read_text()
        if path.name != "verify.py":
            assert not any(re.search(pattern,text) for pattern in secret_patterns), path
        scanned.append(str(path.relative_to(ROOT)))
        if path.suffix == ".json":
            json.loads(text)

    examples = HERE/"examples"
    provenance = load(examples/"provenance.json")
    assert provenance["real_network_calls"] == 0
    assert provenance["versions"] == provenance["historical_versions"]
    for name, expected in provenance["source_files"].items():
        assert sha(ROOT/"docs/validation/private/ai-pretest"/name) == expected
    registry = load(examples/"registry.json")["concepts"]
    retriever = Retriever(registry, method="tfidf")
    traces = []
    for case in provenance["classification_cases"]:
        path = examples/(case.split("/")[-1]+".json")
        data = load(path)
        no_gold(data["payload"])
        assert data["payload"]["private"] is False
        assert data["payload"]["source"] in {"PUBLIC_GITHUB", "SYNTHETIC"}
        assert model_user_payload(data["request"]) == data["payload"]
        assert data["request"]["store"] is False and not data["request"].get("tools")
        assert data["request"]["text"]["format"]["strict"] is True
        assert retriever.candidates(data["profile"]) == data["retrieval"]["shortlist"]
        assert [c["id"] for c in data["payload"]["candidates"]] == data["retrieval"]["shortlist"]
        assert all(set(c)=={"id","kind","name","description"} for c in data["payload"]["candidates"])
        for row in data["retrieval"]["rows"]:
            assert math.isclose(row["score"],row["cosine"]+row["alias_boost"],abs_tol=1e-12)
        validate_classification(Classification.model_validate(data["call"]["result"]),data["validation_context"],registry)
        traces.append(case)
    taxonomy = load(examples/"taxonomy.json")
    no_gold(taxonomy["payload"])
    assert model_user_payload(taxonomy["request"]) == taxonomy["payload"]
    assert len(taxonomy["payload"]["collection"]) == 30
    assert len(taxonomy["call"]["result"]["proposals"]) == 20
    validate_taxonomy(TaxonomyDraft.model_validate(taxonomy["call"]["result"]),{r["repo_id"] for r in taxonomy["payload"]["collection"]})
    fastapi = load(examples/"fastapi.json")
    assert [e["id"] for e in fastapi["payload"]["evidence"]] == ["E0","E1","E2"]
    orion = load(examples/"orion-api.json")
    assert {a["concept_id"] for a in orion["call"]["result"]["assignments"]} == {"p-orion","t-api","g-fastapi","g-python"}
    negated = load(examples/"negated-api.json")
    assert not any(a["kind"]=="PROJECT" for a in negated["call"]["result"]["assignments"])
    replay = load(examples/"lifecycle-replay.json")
    assert not replay["after_analysis"]["edges"]
    assert replay["after_simulated_project_removal"]["protected_rejection"] is True
    assert replay["after_simulated_project_removal"]["admission"][0] is False
    assert replay["after_simulated_project_removal"]["explicit_force_admission"][0] is True
    proposal = load(examples/"jev-proposed-request.json")
    assert proposal["status"] == "UNEXECUTED_PROPOSAL" and "response" not in proposal

    review = load(HERE/"figures/review.json")
    for figure in review["figures"]:
        path = HERE/"figures"/figure["file"]
        assert sha(path) == figure["sha256"]
        assert list(struct.unpack(">II",path.read_bytes()[16:24])) == figure["dimensions"]
    codex_root = Path(os.environ.get("CODEX_HOME", str(Path.home()/".codex")))
    validator = codex_root/"skills/.system/skill-creator/scripts/quick_validate.py"
    assert validator.is_file(), "The installed skill-creator validator is required for this local check"
    skill_check = subprocess.run([sys.executable,str(validator),str(SKILL)],capture_output=True,text=True)
    assert skill_check.returncode == 0, skill_check.stdout+skill_check.stderr
    article = (HERE/"article.md").read_text()
    post = (HERE/"linkedin-post.txt").read_text()
    prior = (ROOT/"ai-system-design/publication/article.md").read_text()
    result = {
        "date":"2026-10-15","status":"PASS" if not failures else "FAIL",
        "scope":"Offline documentation/data verification; editorial scores are self-review judgments",
        "prior_files_byte_identical":len(unchanged),
        "navigation_files_with_original_prefix_preserved":navigation,
        "prior_validation_records_unchanged":len(records),
        "source_manifest_files_unchanged":len(manifest["sha256"]),
        "markdown_files_checked":len(md_files),"local_links_checked":checked,
        "external_https_links_syntax_checked":len(external),"link_failures":failures,
        "text_json_files_scanned":len(scanned),"credential_pattern_check":"PASS",
        "classification_traces":traces,"taxonomy_repository_count":30,
        "historical_logical_request_matches":provenance["logical_cache_matches"],
        "mock_serializations":provenance["mock_serializations"],"real_provider_calls":0,
        "reconstructed_request_payload_identity":"PASS",
        "installed_versions_match_historical":True,"lifecycle_invariants":"PASS",
        "new_figures_checked":len(review["figures"]),"skill_static_validation":skill_check.stdout.strip(),
        "article_words_whitespace":len(article.split()),"v1_words_whitespace":len(prior.split()),
        "estimated_read_minutes_at_225_wpm":round(len(article.split())/225,1),
        "linkedin_characters":len(post.rstrip("\n")),"linkedin_words":len(post.split()),
        "engagement_or_independent_reader_evidence":"Not measured",
        "wire_capture_limit":"Current mock captures, not original historical HTTP bodies",
        "provider_experiments":"No new OpenAI or Jev generations; historical results preserved",
    }
    rendering = HERE/"rendering-review.json"
    if rendering.exists():
        result["rendering"] = load(rendering)
    (HERE/"verification.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k not in {"classification_traces","rendering","wire_capture_limit","navigation_files_with_original_prefix_preserved","provider_experiments"}}))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

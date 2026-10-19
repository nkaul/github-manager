"""Offline contract, blindness, provenance and exact-evidence regression checks."""

import copy
import json

import pytest

from app.demo import annotation_pilot as pilot


@pytest.fixture
def corpus(tmp_path):
    root = tmp_path
    release = root / pilot.DATA / "release"
    release.mkdir(parents=True)
    source = root / pilot.DATA / "sources" / "shared" / "README.md"
    source.parent.mkdir(parents=True)
    source.write_text("A dedicated Widget extension.\nProvides event processing in Python.\n")
    source_raw = source.read_bytes()
    source_info = {
        "path": "README.md",
        "role": "README",
        "local_path": str(source.relative_to(root)),
        "sha256": pilot.sha(source_raw),
        "bytes": len(source_raw),
        "git_blob_sha": "fixture-blob",
        "source_url": "https://github.com/public/widget/blob/fixture/README.md",
    }
    registry = {
        "domain:fixture": {
            "id": "domain:fixture",
            "kind": "DOMAIN",
            "name": "Fixture domain",
            "description": "Fixture only",
            "aliases": [],
            "domain": None,
        },
        "project:widget": {
            "id": "project:widget",
            "kind": "PROJECT",
            "name": "Widget",
            "description": "Widget and dedicated extensions",
            "aliases": [],
            "domain": "domain:fixture",
        },
        "topic:events": {
            "id": "topic:events",
            "kind": "TOPIC",
            "name": "Event processing",
            "description": "Primary event processing",
            "aliases": [],
            "domain": None,
        },
        "tag:python": {
            "id": "tag:python",
            "kind": "TAG",
            "name": "Python",
            "description": "Python technology",
            "aliases": [],
            "domain": None,
        },
    }
    inventory, groups = [], []
    source_hashes = {source_info["local_path"]: source_info["sha256"]}
    for rid in range(1, 601):
        domain = f"bucket-{(rid - 1) // 60}"
        split = "development" if (rid - 1) % 60 < 30 else "test_reserved"
        path = root / pilot.DATA / "shards" / "fixture" / f"{rid}.json"
        value = {
            "numeric_id": rid,
            "commit": "fixture-commit",
            "private": False,
            "full_name": f"public/widget-{rid}",
            "url": f"https://github.com/public/widget-{rid}",
            "description": "Saved GitHub description",
            "readme": source_info,
            "supporting_files": [],
            "annotations": {"purpose": "BLINDNESS_SENTINEL", "labels": ["HIDDEN_OLD_LABEL"]},
        }
        pilot.save(path, value)
        local = str(path.relative_to(root))
        source_hashes[local] = pilot.sha(path.read_bytes())
        inventory.append(
            {
                "repository_id": rid,
                "full_name": value["full_name"],
                "sampling_domain": domain,
                "split": split,
                "group": f"group:{rid}",
                "commit": value["commit"],
                "dossier_path": local,
            }
        )
        groups.append({"id": f"group:{rid}", "split": split, "repository_ids": [rid]})
    (release / "inventory.jsonl").write_text("".join(json.dumps(row) + "\n" for row in inventory))
    pilot.save(release / "registry.proposed.json", registry)
    pilot.save(release / "splits.provisional.json", {"groups": groups})
    manifest = {
        "repositories": 600,
        "status": "PROPOSED_REFERENCES_NOT_GOLD",
        "release_id": "fixture-v2",
        "sources_and_dossiers_sha256": source_hashes,
        "release_files": {
            name: {
                "sha256": pilot.sha((release / name).read_bytes()),
                "bytes": (release / name).stat().st_size,
            }
            for name in ("inventory.jsonl", "registry.proposed.json", "splits.provisional.json")
        },
    }
    pilot.save(release / "manifest.local.json", manifest)
    pilot.prepare(root)
    return root


def annotation(root, agent="a", entry=None, label_ids=None):
    selection = json.loads((root / pilot.OUTPUT / "selection.json").read_bytes())
    entry = entry or selection["repositories"][0]
    packet = json.loads((root / entry["packet_path"]).read_bytes())
    source = next(s for s in packet["sources"] if s["path"] == "README.md")
    citation = {
        "path": "README.md",
        "sha256": source["sha256"],
        "quote": "A dedicated Widget extension.",
        "start_line": 1,
        "end_line": 1,
    }
    label_ids = label_ids or ["project:widget", "topic:events", "tag:python"]
    return {
        "schema_version": "1.0",
        "repository_id": entry["repository_id"],
        "packet_sha256": entry["packet_sha256"],
        "producer": {
            "agent_id": agent,
            "runtime": "Codex",
            "model": None,
            "model_description": "Exact serving model unavailable in test fixture",
            "independent_source_first": True,
            "source_packet_only": True,
            "external_api_calls": 0,
            "incremental_api_cost_usd": 0,
            "agent_allowance": "unmeasured",
        },
        "purpose": "A dedicated Widget extension that provides event processing in Python.",
        "purpose_evidence": [citation],
        "positive_ids": label_ids,
        "labels": [
            {
                "id": cid,
                "rationale": "Fixture source evidence supports this test concept.",
                "evidence": [citation],
            }
            for cid in label_ids
        ],
        "source_reading": [
            {
                "path": s["path"],
                "sha256": s["sha256"],
                "intervals": [[1, s["lines"]]],
                "complete": True,
                "note": "Fixture fully read for contract testing.",
            }
            for s in packet["sources"]
        ],
        "group_scope": {
            kind: {
                "status": "COMPLETE_WITHIN_SAVED_SCOPE",
                "reason": "All fixture sources and known definitions reviewed.",
            }
            for kind in ("projects", "topics", "tags")
        },
        "conflicts": [],
        "missing_concepts": [],
        "caveats": ["Synthetic test annotation, never production labels."],
    }


def test_prepare_is_reproducible_blind_development_only_and_read_only(corpus):
    selection_path = corpus / pilot.OUTPUT / "selection.json"
    before = selection_path.read_bytes()
    release = corpus / pilot.DATA / "release"
    frozen = {p.name: p.read_bytes() for p in release.iterdir()}
    selection = pilot.prepare(corpus)
    assert before == selection_path.read_bytes()
    assert len(selection["repositories"]) == 30
    assert set(selection["counts"].values()) == {3}
    assert {entry["split"] for entry in selection["repositories"]} == {"development"}
    for entry in selection["repositories"]:
        packet_raw = (corpus / entry["packet_path"]).read_bytes()
        assert b"BLINDNESS_SENTINEL" not in packet_raw
        assert b"HIDDEN_OLD_LABEL" not in packet_raw
        assert b"source_packet_only" not in packet_raw
    assert frozen == {p.name: p.read_bytes() for p in release.iterdir()}
    assert pilot.load_sidecar(corpus)["status"] == "READY_FOR_INDEPENDENT_AGENTS"
    app_state = pilot.read_sidecar(corpus, release)
    assert app_state["state"] == "PARTIAL"
    assert app_state["summary"]["human_queue"] == {}


@pytest.mark.parametrize(
    "mutation, message",
    [
        (
            lambda v: v["labels"][0]["evidence"][0].update(quote="Invented exact quotation"),
            "exact quote",
        ),
        (lambda v: v["labels"][0]["evidence"][0].update(start_line=2, end_line=2), "exact quote"),
        (lambda v: v["labels"][0]["evidence"][0].update(sha256="0" * 64), "source/hash"),
        (lambda v: v.update(repository_id=999999), "selected development"),
        (lambda v: v.update(packet_sha256="0" * 64), "packet binding"),
        (
            lambda v: v.update(
                labels=[dict(v["labels"][0], id="domain:fixture")], positive_ids=["domain:fixture"]
            ),
            "nonselectable",
        ),
        (
            lambda v: v.update(
                labels=[dict(v["labels"][0], id="topic:invented")], positive_ids=["topic:invented"]
            ),
            "nonselectable",
        ),
        (lambda v: v["positive_ids"].append(v["positive_ids"][0]), "unique"),
        (lambda v: v["producer"].update(independent_source_first=False), "Independent producer"),
        (lambda v: v["source_reading"][0].update(intervals=[], complete=True), "completeness"),
        (lambda v: v["source_reading"].pop(), "every supplied source"),
        (lambda v: v.update(human_confidence=0.99), "Extra inputs"),
        (lambda v: v.update(negative_ids=["topic:events"]), "Extra inputs"),
    ],
)
def test_rejects_fabricated_or_unbound_annotations(corpus, mutation, message):
    value = annotation(corpus)
    mutation(value)
    with pytest.raises(ValueError, match=message):
        pilot.validate_annotation(corpus, value, "a")


def test_partial_reading_cannot_claim_complete_scope(corpus):
    value = annotation(corpus)
    metadata = value["source_reading"][0]
    metadata.update(intervals=[], complete=False, note="Not read")
    with pytest.raises(ValueError, match="Complete scope"):
        pilot.validate_annotation(corpus, value, "a")
    for scope in value["group_scope"].values():
        scope["status"] = "PARTIAL"
    assert pilot.validate_annotation(corpus, value, "a")["source_reading"][0]["complete"] is False


def test_quote_must_be_within_declared_reading(corpus):
    value = annotation(corpus)
    value["source_reading"][1].update(intervals=[[2, 2]], complete=False)
    with pytest.raises(ValueError, match="declared semantic reading"):
        pilot.validate_annotation(corpus, value, "a")


def test_mutated_retained_bytes_are_rejected_on_import_and_app_load(corpus):
    value = annotation(corpus)
    path = corpus / pilot.DATA / "sources" / "shared" / "README.md"
    path.write_text(path.read_text() + "tampered\n")
    with pytest.raises(ValueError, match="Integrity"):
        pilot.validate_annotation(corpus, value, "a")
    with pytest.raises(ValueError, match="Integrity"):
        pilot.load_sidecar(corpus)
    assert pilot.read_sidecar(corpus)["state"] == "INVALID"
    assert pilot.read_sidecar(corpus)["records"] == {}


def test_import_is_all_or_nothing_and_comparison_keeps_unknown_omissions(corpus):
    entries = json.loads((corpus / pilot.OUTPUT / "selection.json").read_bytes())["repositories"]
    for agent in ("a", "b"):
        values = [annotation(corpus, agent, entry) for entry in entries]
        if agent == "b":
            values[0]["labels"] = values[0]["labels"][:1]
            values[0]["positive_ids"] = ["project:widget"]
        path = corpus / pilot.OUTPUT / f"fixture-{agent}.jsonl"
        path.write_text("".join(json.dumps(v) + "\n" for v in values))
        if agent == "a":
            incomplete = corpus / pilot.OUTPUT / "incomplete.jsonl"
            incomplete.write_text(json.dumps(values[0]) + "\n")
            with pytest.raises(ValueError, match="all 30"):
                pilot.import_annotations(corpus, agent, incomplete)
            assert not (corpus / pilot.OUTPUT / "agent-a.validated.json").exists()
        pilot.import_annotations(corpus, agent, path)
    result = pilot.compare(corpus)
    comparison = result["records"][str(entries[0]["repository_id"])]["comparison"]
    assert comparison["a_only_ids"] == ["tag:python", "topic:events"]
    assert comparison["review_band"] == "AMBER"
    assert comparison["derived_domains"] == ["domain:fixture"]
    assert result["summary"]["review_bands"] == {"AMBER": 1, "GREEN": 29}
    assert result["summary"]["human_confirmed"] == 0
    assert sum(result["summary"]["human_queue"].values()) == 20
    assert result["provenance"]["external_api_calls"] == 0
    assert "negative_ids" not in json.dumps(result)
    assert pilot.load_sidecar(corpus)["summary"] == result["summary"]
    raw = (corpus / pilot.OUTPUT / "review.json").read_bytes()
    pilot.compare(corpus)
    assert (corpus / pilot.OUTPUT / "review.json").read_bytes() == raw
    path = corpus / pilot.OUTPUT / "review.json"
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ValueError, match="Integrity"):
        pilot.load_sidecar(corpus)


def test_sidecar_path_traversal_rejected(corpus):
    manifest_path = corpus / pilot.OUTPUT / "manifest.json"
    value = json.loads(manifest_path.read_bytes())
    value["files"]["../../escape"] = copy.deepcopy(next(iter(value["files"].values())))
    pilot.save(manifest_path, value)
    with pytest.raises(ValueError, match="path rejected"):
        pilot.load_sidecar(corpus)


def test_missing_and_wrong_release_states_are_safe(tmp_path):
    assert pilot.read_sidecar(tmp_path)["state"] == "NOT_RUN"
    assert pilot.read_sidecar(tmp_path, tmp_path / "other-release")["state"] == "INVALID"

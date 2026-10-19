"""Read-only source and workspace verification after the authorized evaluation."""

import hashlib
import json
import sqlite3
import zipfile
from datetime import UTC, datetime

from runner import OUT, ROOT, corpus, historical_sha256, read, repo_path, save, source_hash, verify  # isort: skip


def main():
    verify()
    baseline = read(ROOT / ".tools/ground-truth-evaluation-plan-preservation-before.json")
    c = corpus()
    source_failures = [
        relative
        for relative, expected in c.manifest["sources_and_dossiers_sha256"].items()
        if source_hash(ROOT / relative) != expected
    ]
    with sqlite3.connect(
        f"{(ROOT / 'docs/validation/private/demo/app.sqlite3').as_uri()}?mode=ro", uri=True
    ) as db:
        workspace_hashes = {
            key: hashlib.sha256(value.encode()).hexdigest()
            for key, value in db.execute("SELECT id,state FROM workspace")
        }
        live_states = {
            key: json.loads(value) for key, value in db.execute("SELECT id,state FROM workspace")
        }
    changed_workspaces = [
        key
        for key in set(workspace_hashes) | set(baseline["workspaces"])
        if workspace_hashes.get(key) != baseline["workspaces"].get(key)
    ]
    frozen = read(OUT / "reference-snapshot.json")
    reference_owners = [
        state
        for state in live_states.values()
        if state.get("reference_reviews", {}).get(c.manifest["release_id"])
    ]
    assert len(reference_owners) == 1
    current_reviews = reference_owners[0]["reference_reviews"][c.manifest["release_id"]]
    package = ROOT / "eval/ai-system-design/ground-truth-creation"
    archive = read(package / "history/pre-evaluation-plan-preservation-2026-10-19.json")
    archive_path = package / "history" / archive["archive"]
    with zipfile.ZipFile(archive_path) as snapshot:
        files = archive["files"]
        intact = all(
            hashlib.sha256(snapshot.read(row["path"])).hexdigest() == row["sha256"] for row in files
        )
    prior_artifacts = read(ROOT / ".tools/create-assign-preservation-before.json")["files"]
    prior_artifact_changes = [
        relative
        for relative, expected in prior_artifacts.items()
        if not repo_path(relative).is_file() or historical_sha256(repo_path(relative)) != expected
    ]
    checks = {
        "immutable_evaluation_inputs_and_producer_hashes": True,
        "source_and_dossier_hashes": not source_failures,
        "source_manifest_hash": c._manifest_hash == baseline["source_manifest_sha256"],
        "ground_truth_and_sample_workspace_raw_states": all(
            key.endswith(":github") for key in changed_workspaces
        ),
        "all_frozen_human_review_records_equal_current": current_reviews
        == {rid: case["review"] for rid, case in frozen.items()},
        "effective_registry_history_equal_current": c.registry_adapter().export(reference_owners[0])
        == read(OUT / "registry-history.json"),
        "pre_evaluation_publication_archive_hash": source_hash(archive_path) == archive["sha256"],
        "pre_evaluation_publication_archive_members": intact,
        "prior_readiness_benchmark_and_pilot_artifacts": not prior_artifact_changes,
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "captured_at_utc": datetime.now(UTC).isoformat(),
        "checks": checks,
        "manifest_bound_sources_and_dossiers_checked": len(
            c.manifest["sources_and_dossiers_sha256"]
        ),
        "source_failures": source_failures,
        "workspaces_checked": len(workspace_hashes),
        "live_workspace_observation": {
            "all_raw_states_equal_baseline": not changed_workspaces,
            "changed_workspace_types": [key.split(":")[-1] for key in changed_workspaces],
            "github_synced_at": next(
                (
                    s.get("core", {}).get("synced_at")
                    for k, s in live_states.items()
                    if k.endswith(":github")
                ),
                None,
            ),
            "scope": "Evaluation opens app SQLite read-only. A later live GitHub sync can change its workspace; that observation is retained and is not rolled back. Ground Truth/sample states and all reference records are checked separately.",
        },
        "prior_protected_artifacts_checked": len(prior_artifacts),
        "prior_artifact_changes": prior_artifact_changes,
        "ledger_boundary": "The monetary SQLite database changed intentionally for the approved 50 evaluations. The 91 historical call rows and their total charges are separately recounted; unchanged database bytes are not claimed.",
    }
    save("preservation-check.json", result)
    print(json.dumps(result, indent=2))
    assert result["status"] == "PASS"


if __name__ == "__main__":
    main()

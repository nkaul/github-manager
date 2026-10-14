import pytest

from app.pretest.ai.corpus import registry
from app.pretest.ai.organization import LocalOrganizationRun


def test_partial_run_preserves_manual_decisions_and_successful_proposals():
    run = LocalOrganizationRun(
        ["a", "b", "c"], registry(), manual={"a": ["p-audit"]}, rejected={"a": ["p-helios"]}
    )
    run.start()
    run.record("a", ["p-orion", "p-helios", "p-audit"])
    run.record("b", ["p-helios"], failed=True)
    run.record("c", [])
    result = run.finish()
    assert result["state"] == "PARTIAL_FAILED"
    assert result["repos"]["a"]["USER"] == ["p-audit"]
    assert result["repos"]["a"]["PROPOSED"] == ["p-orion"]
    assert result["repos"]["b"]["PROPOSED"] == []
    assert result["counts"] == {
        "processed_repos": 3,
        "failed_repos": 1,
        "manual_repos": 1,
        "proposed_repos": 1,
        "uncategorized_repos": 1,
    }
    assert result["canonical_published"] is False and result["github_mutations"] == 0
    with pytest.raises(ValueError):
        run.record("a", ["p-helios"])


def test_local_run_rejects_early_finish_duplicate_and_invalid_results():
    run = LocalOrganizationRun(["a", "b"], registry())
    with pytest.raises(ValueError):
        run.record("a", [])
    run.start()
    with pytest.raises(ValueError):
        run.finish()
    with pytest.raises(ValueError):
        run.record("a", ["unknown"])
    run.record("a", ["p-orion"])
    with pytest.raises(ValueError):
        run.record("a", ["p-orion"])
    run.record("b", [])
    assert run.finish()["state"] == "COMPLETED"

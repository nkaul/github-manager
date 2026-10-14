import re
from datetime import UTC, datetime, timedelta
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from app.github.client import GitHubError


class RepoFixture(BaseModel):
    model_config = ConfigDict(extra="forbid")
    alias: str = Field(pattern=r"^[a-z0-9-]{1,40}$")
    repo_id: int | None = Field(default=None, gt=0)
    full_name: str | None = Field(default=None, pattern=r"^[A-Za-z0-9-]+/[A-Za-z0-9_.-]+$")
    expected_sources: list[str] = Field(default_factory=list)
    eligible: bool
    favorite: bool | None = None
    readme_present: bool | None = None
    recent_commit_by_user: bool = False
    private: bool | None = None
    contents_access: bool = False

    @model_validator(mode="after")
    def identity_required(self):
        if not self.repo_id and not self.full_name:
            raise ValueError("Supply a known ID or owner/repo name")
        if self.full_name and self.full_name.split("/")[1] in {".", ".."}:
            raise ValueError("Invalid repository name")
        return self


class OrganizationFixture(BaseModel):
    model_config = ConfigDict(extra="forbid")
    alias: str = Field(pattern=r"^[a-z0-9-]{1,40}$")
    login: str = Field(pattern=r"^[A-Za-z0-9-]+$")
    expected_repository_ids: list[int] = Field(default_factory=list, max_length=1000)
    exact_accessible_set: bool = False


class Fixtures(BaseModel):
    model_config = ConfigDict(extra="forbid")
    repositories: list[RepoFixture] = Field(max_length=20)
    organizations: list[OrganizationFixture] = Field(default_factory=list, max_length=10)
    sample_private_repositories: int = Field(default=0, ge=0, le=3)
    sample_member_organizations: int = Field(default=0, ge=0, le=2)


def row(check, status, detail):
    return {"check": check, "evidence": "LIVE", "status": status, "detail": detail}


async def organization_checks(fixture, snapshot, adapter, token):
    rows = []
    try:
        membership, _ = await adapter.request(token, f"/user/memberships/orgs/{fixture.login}")
        active = membership.get("state") == "active"
        rows.append(
            row(
                fixture.alias + "/membership",
                "PASS" if active else "FAIL",
                "Active membership confirmed" if active else "Membership is not active",
            )
        )
        values, capped = await adapter.pages(token, f"/orgs/{fixture.login}/repos", type="all")
        observed = {value["id"] for value in values if isinstance(value.get("id"), int)}
        discovered = {repo["id"] for repo in snapshot["repos"]}
        expected = set(fixture.expected_repository_ids)
        matches = not capped and expected <= observed and expected <= discovered
        if fixture.exact_accessible_set:
            matches = matches and observed == expected
        rows.append(
            row(
                fixture.alias + "/expected-repositories",
                "PASS" if matches and expected else "FAIL" if expected else "NOT_TESTED",
                f"Expected {len(expected)}; observed accessible {len(observed)}; "
                + (
                    "complete independently supplied set"
                    if fixture.exact_accessible_set
                    else "subset check; no independently supplied complete organization set"
                ),
            )
        )
        missing = observed - discovered
        rows.append(
            row(
                fixture.alias + "/discovery-cross-check",
                "BLOCKED" if capped else "FAIL" if missing else "PASS",
                f"Organization API IDs={len(observed)}; missing from inventory={len(missing)}; "
                "checks visibility under this token, not repositories hidden by policy",
            )
        )
    except GitHubError as exc:
        rows.append(
            row(
                fixture.alias + "/organization-access",
                "FAIL",
                exc.category + ("; SSO authorization required" if exc.sso else ""),
            )
        )
    return rows


async def fixture_checks(path: Path | None, snapshot, adapter, token):
    if not path:
        return [
            {
                "check": "Known-fixture matrix",
                "evidence": "POLICY",
                "status": "BLOCKED",
                "detail": "Set GITHUB_FIXTURES_FILE with known IDs; counts do not prove coverage",
            }
        ]
    try:
        fixtures = Fixtures.model_validate_json(path.read_text())
    except (OSError, ValidationError):
        return [
            {
                "check": "Known-fixture matrix",
                "evidence": "POLICY",
                "status": "BLOCKED",
                "detail": "Fixture manifest missing or invalid; identifiers and contents omitted",
            }
        ]
    rows = []
    repos = {r["id"]: r for r in snapshot["repos"]}
    repository_fixtures = list(fixtures.repositories)
    private_samples = [repo for repo in snapshot["repos"] if repo["private"]][
        : fixtures.sample_private_repositories
    ]
    for index, sample in enumerate(private_samples):
        repository_fixtures.append(
            RepoFixture(
                alias=f"private-sample-{index + 1}",
                repo_id=sample["id"],
                full_name=sample["full_name"],
                expected_sources=sample["sources"],
                eligible=sample["eligible"],
                private=True,
                contents_access=True,
            )
        )
    if fixtures.sample_private_repositories:
        rows.append(
            row(
                "Private sample availability",
                "PASS" if private_samples else "BLOCKED",
                f"Selected {len(private_samples)} accessible private examples; "
                "sampling does not prove discovery of every private repository",
            )
        )
    for fixture in repository_fixtures:
        repo = repos.get(fixture.repo_id)
        if fixture.full_name:
            try:
                metadata, _ = await adapter.request(token, f"/repos/{fixture.full_name}")
                identity_matches = isinstance(metadata.get("id"), int) and (
                    fixture.repo_id is None or metadata["id"] == fixture.repo_id
                )
                privacy_matches = (
                    fixture.private is None or metadata.get("private") == fixture.private
                )
                rows.append(
                    row(
                        fixture.alias + "/metadata",
                        "PASS" if identity_matches and privacy_matches else "FAIL",
                        "Direct metadata ID/visibility matched; private="
                        + str(metadata.get("private"))
                        + "; names omitted",
                    )
                )
                repo = repos.get(metadata.get("id")) if identity_matches else None
            except GitHubError as exc:
                rows.append(
                    row(
                        fixture.alias + "/metadata",
                        "FAIL",
                        exc.category + ("; SSO authorization required" if exc.sso else ""),
                    )
                )
                repo = None
        matches = (
            repo is not None
            and repo["eligible"] == fixture.eligible
            and set(fixture.expected_sources) <= set(repo["sources"])
            and (fixture.favorite is None or repo["favorite"] == fixture.favorite)
            and (fixture.private is None or repo["private"] == fixture.private)
        )
        rows.append(
            {
                "check": fixture.alias + "/discovery",
                "evidence": "LIVE",
                "status": "PASS" if matches else "FAIL",
                "detail": "Expected identity/source/eligibility/favorite matched"
                if matches
                else "Fixture missing or source/policy mismatch; confirm grant, scopes and org/SSO",
            }
        )
        if not repo or not re.fullmatch(r"[\w.-]+/[\w.-]+", repo["full_name"]):
            continue
        if fixture.contents_access:
            try:
                value, _ = await adapter.request(token, f"/repos/{repo['full_name']}/contents")
                matches = isinstance(value, list)
                rows.append(
                    row(
                        fixture.alias + "/contents",
                        "PASS" if matches else "FAIL",
                        "Repository root Contents API accessible; response discarded",
                    )
                )
            except GitHubError as exc:
                rows.append(row(fixture.alias + "/contents", "FAIL", exc.category))
        if fixture.readme_present is not None or fixture.contents_access:
            try:
                value, _ = await adapter.request(token, f"/repos/{repo['full_name']}/readme")
                matches = fixture.readme_present is not False and isinstance(
                    value.get("content"), str
                )
                detail = "README endpoint accessible; body discarded and not sent to a model"
                status = "PASS" if matches else "FAIL"
            except GitHubError as exc:
                matches = not fixture.readme_present and exc.status == 404
                detail = exc.category + "; 404 can also mean hidden; expectation came from manifest"
                status = (
                    "NOT_TESTED"
                    if fixture.readme_present is None and exc.status == 404
                    else "PASS"
                    if matches
                    else "FAIL"
                )
            rows.append(
                {
                    "check": fixture.alias + "/readme",
                    "evidence": "LIVE",
                    "status": status,
                    "detail": detail,
                }
            )
        if fixture.recent_commit_by_user:
            try:
                since = (datetime.now(UTC) - timedelta(days=14)).isoformat()
                values, _ = await adapter.request(
                    token,
                    f"/repos/{repo['full_name']}/commits",
                    params={
                        "author": snapshot["identity"]["login"],
                        "since": since,
                        "per_page": 10,
                    },
                )
                matches = any(
                    (v.get("author") or {}).get("id") == snapshot["identity"]["id"] for v in values
                )
                detail = (
                    "Numeric actor match observed"
                    if matches
                    else "No numeric actor match in bounded 14-day/10-commit sample"
                )
            except GitHubError as exc:
                matches, detail = False, exc.category
            rows.append(
                {
                    "check": fixture.alias + "/activity",
                    "evidence": "LIVE",
                    "status": "PASS" if matches else "FAIL",
                    "detail": detail,
                }
            )
    organizations = list(fixtures.organizations)
    if fixtures.sample_member_organizations:
        try:
            memberships, capped = await adapter.pages(token, "/user/orgs")
            rows.append(
                row(
                    "Organization enumeration",
                    "BLOCKED" if capped else "PASS",
                    f"Authenticated organization memberships={len(memberships)}; "
                    "hidden/denied memberships cannot be inferred",
                )
            )
            known = {fixture.login.lower() for fixture in organizations}
            samples = [
                item
                for item in memberships
                if re.fullmatch(r"[A-Za-z0-9-]+", item.get("login", ""))
                and item["login"].lower() not in known
            ][: fixtures.sample_member_organizations]
            organizations += [
                OrganizationFixture(alias=f"organization-sample-{index + 1}", login=item["login"])
                for index, item in enumerate(samples)
            ]
            if not organizations:
                rows.append(
                    row(
                        "Representative organizations",
                        "BLOCKED",
                        "No accessible organization memberships available for sampling",
                    )
                )
        except GitHubError as exc:
            rows.append(row("Organization enumeration", "FAIL", exc.category))
    for fixture in organizations:
        rows.extend(await organization_checks(fixture, snapshot, adapter, token))
    if not repository_fixtures:
        rows.append(
            {
                "check": "Known-fixture matrix",
                "evidence": "POLICY",
                "status": "BLOCKED",
                "detail": "No expected repository fixtures supplied",
            }
        )
    return rows

from typing import Literal

from pydantic import BaseModel, ConfigDict

Kind = Literal["DOMAIN", "PROJECT", "TOPIC", "TAG"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Assignment(StrictModel):
    kind: Kind
    concept_id: str
    confidence: float
    evidence_ids: list[str]
    reason: str


class Classification(StrictModel):
    status: Literal["CLASSIFIED", "NO_MATCH", "NEEDS_MORE_CONTEXT"]
    assignments: list[Assignment]
    summary: str


class Proposal(StrictModel):
    kind: Kind
    name: str
    description: str
    aliases: list[str]
    parent_domain: str | None
    supporting_repo_ids: list[str]


class TaxonomyDraft(StrictModel):
    proposals: list[Proposal]
    notes: str


class AccessProbe(StrictModel):
    authenticated: bool
    category: Literal["TEST"]


def validate_classification(result, context, registry):
    if context["revision"] != context["active_revision"]:
        raise ValueError("Stale taxonomy revision")
    if context["profile_hash"] != context["active_profile_hash"]:
        raise ValueError("Stale profile")
    if context.get("policy_version", 1) != context.get("active_policy_version", 1):
        raise ValueError("Stale privacy policy")
    if len(result.assignments) > 12 or len(result.summary) > 300:
        raise ValueError("Oversized classification")
    if (result.status == "CLASSIFIED") != bool(result.assignments):
        raise ValueError("Inconsistent classification status")
    seen = set()
    for item in result.assignments:
        concept = registry.get(item.concept_id)
        if (
            not concept
            or concept["kind"] != item.kind
            or not concept.get("active", True)
            or concept.get("workspace", "fixture") != context["workspace"]
            or item.concept_id not in context["candidates"]
            or item.concept_id in seen
            or item.kind == "DOMAIN"
            or item.concept_id in context.get("rejections", [])
        ):
            raise ValueError("Invalid or disallowed canonical assignment")
        if not 0 <= item.confidence <= 1 or len(item.reason) > 240:
            raise ValueError("Invalid confidence/reason")
        if not item.evidence_ids or len(item.evidence_ids) > 5:
            raise ValueError("Missing/oversized evidence")
        if not set(item.evidence_ids) <= set(context["evidence_ids"]):
            raise ValueError("Invented evidence reference")
        seen.add(item.concept_id)
    return result


def validate_taxonomy(draft, repo_ids):
    if len(draft.proposals) > 50 or len(draft.notes) > 800:
        raise ValueError("Oversized taxonomy draft")
    names = set()
    domains = {p.name.casefold() for p in draft.proposals if p.kind == "DOMAIN"}
    for proposal in draft.proposals:
        key = (proposal.kind, " ".join(proposal.name.casefold().split()))
        if key in names or not key[1] or len(proposal.name) > 100:
            raise ValueError("Duplicate/invalid proposal name")
        if len(proposal.description) > 300 or len(proposal.aliases) > 6:
            raise ValueError("Oversized proposal")
        if not proposal.supporting_repo_ids or not set(proposal.supporting_repo_ids) <= repo_ids:
            raise ValueError("Invalid supporting repository")
        if proposal.kind == "PROJECT" and (
            not proposal.parent_domain or proposal.parent_domain.casefold() not in domains
        ):
            raise ValueError("Project requires a proposed domain")
        if proposal.kind != "PROJECT" and proposal.parent_domain is not None:
            raise ValueError("Only projects carry parent_domain")
        names.add(key)
    return draft

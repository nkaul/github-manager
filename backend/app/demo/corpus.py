"""Read-only versioned public evidence and owner-scoped human review records."""

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.demo.corpus_registry import CorpusRegistry, RegistryContext
from app.demo.store import Store


class Citation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    path: str = Field(min_length=1, max_length=500)
    quote: str = Field(min_length=1, max_length=10000)


class Dimensions(BaseModel):
    model_config = ConfigDict(extra="forbid")
    projects: bool
    topics: bool
    tags: bool


class CorpusReview(BaseModel):
    model_config = ConfigDict(extra="forbid")
    release_id: str = Field(max_length=200)
    manifest_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    expected_revision: int = Field(ge=0)
    status: Literal["HUMAN_CONFIRMED", "NEEDS_REVIEW", "UNRESOLVED"]
    purpose: str = Field(max_length=10000)
    label_ids: list[str] = Field(max_length=100)
    dimensions: Dimensions
    additional_evidence: dict[str, Citation] = Field(default_factory=dict, max_length=100)
    notes: str = Field(default="", max_length=10000)
    annotation_pilot_sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    expected_draft_revision: int | None = Field(default=None, ge=0)
    registry_context: RegistryContext | None = None


class DraftCitation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    path: str = Field(default="", max_length=500)
    quote: str = Field(default="", max_length=10000)


class CorpusDraft(BaseModel):
    """An incomplete buffer, deliberately separate from final reference reviews."""

    model_config = ConfigDict(extra="forbid")
    release_id: str = Field(max_length=200)
    manifest_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    expected_revision: int = Field(ge=0)
    base_review_revision: int = Field(ge=0)
    purpose: str = Field(default="", max_length=10000)
    label_ids: list[str] = Field(default_factory=list, max_length=100)
    dimensions: Dimensions = Field(
        default_factory=lambda: Dimensions(projects=False, topics=False, tags=False)
    )
    additional_evidence: dict[str, DraftCitation] = Field(default_factory=dict, max_length=100)
    notes: str = Field(default="", max_length=10000)
    status: Literal["HUMAN_CONFIRMED", "NEEDS_REVIEW", "UNRESOLVED"] = "NEEDS_REVIEW"
    annotation_pilot_sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")

    registry_context: RegistryContext | None = None


class CorpusConflict(ValueError):
    def __init__(self, message, code, current_review=None, current_draft=None):
        super().__init__(message)
        self.code, self.current_review, self.current_draft = code, current_review, current_draft


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()


def merged_labels(proposal):
    """One visible label per decision; retain independent source/metadata proofs."""
    grouped = {}
    for label in proposal["labels"]:
        key = (label["id"], label.get("decision", "SUPPORTED"))
        if key not in grouped:
            grouped[key] = {**label, "evidence": [], "rationale": ""}
        item = grouped[key]
        for evidence in label.get("evidence", []):
            if evidence not in item["evidence"]:
                item["evidence"].append(evidence)
        rationale = label.get("rationale") or ""
        if rationale and rationale not in item["rationale"]:
            item["rationale"] = "; ".join(filter(None, (item["rationale"], rationale)))
    return list(grouped.values())


class Corpus:
    def __init__(self, root: Path, release: Path, store: Store):
        self.root, self.release, self.store = root.resolve(), release.resolve(), store
        self._manifest_hash = None

    def registry_adapter(self):
        self.load()
        return CorpusRegistry(self.registry, self._manifest_hash, self.manifest["release_id"])

    def registry_view(self, workspace):
        return self.registry_adapter().view(self.store.read(workspace))

    def create_registry_concept(self, workspace, value, actor):
        adapter = self.registry_adapter()
        return self.store.mutate(workspace, lambda state: adapter.create(state, value, actor))

    def export_registry(self, workspace):
        return self.registry_adapter().export(self.store.read(workspace))

    def annotation_pilot(self):
        from app.demo.annotation_pilot import read_sidecar

        return read_sidecar(self.root, self.release)

    def metadata_source(self, rid, pilot=None):
        pilot = pilot if pilot is not None else self.annotation_pilot()
        annotation = pilot.get("records", {}).get(str(rid), {}).get("annotations", {}).get("a", {})
        if pilot["state"] != "READY" or not any(
            source["path"] == "@github-metadata.json"
            for source in annotation.get("source_reading", [])
        ):
            return None
        from app.demo.annotation_pilot import source_packet

        packet = source_packet(self.root, self.manifest, self._manifest_hash, self.inventory[rid])
        metadata = next(
            source for source in packet["sources"] if source["role"] == "GITHUB_METADATA"
        )
        return {
            **{key: metadata[key] for key in ("path", "sha256", "bytes", "role", "text")},
            "commit": self.inventory[rid]["commit"],
        }

    def annotation_pilot_summary(self, reviews):
        pilot = self.annotation_pilot()
        records = pilot.get("records", {})
        queue = []
        for row in records.values():
            queue.append(
                {
                    "repository_id": row["repository_id"],
                    "full_name": row["full_name"],
                    "sampling_domain": row["sampling_domain"],
                    "review_band": row["comparison"]["review_band"],
                    "audit_selection": row["audit_selection"],
                    "review_status": reviews.get(str(row["repository_id"]), {}).get(
                        "status", "PROPOSED"
                    ),
                }
            )
        return {
            key: pilot[key]
            for key in (
                "state",
                "status",
                "summary",
                "provenance",
                "pilot_id",
                "sidecar_manifest_sha256",
                "reason",
            )
            if key in pilot
        } | {
            "queue": queue,
            "reviewed_by_you": sum(str(row["repository_id"]) in reviews for row in queue),
            "confirmed_by_you": sum(row["review_status"] == "HUMAN_CONFIRMED" for row in queue),
        }

    def load(self):
        path = self.release / "manifest.local.json"
        if not path.exists():
            raise ValueError(
                "The English corpus release is not ready yet. "
                "Please finish corpus validation first."
            )
        raw = path.read_bytes()
        manifest_hash = hashlib.sha256(raw).hexdigest()
        if manifest_hash == self._manifest_hash:
            return
        manifest = json.loads(raw)
        if (
            manifest.get("status") != "PROPOSED_REFERENCES_NOT_GOLD"
            or manifest.get("repositories") != 600
        ):
            raise ValueError("Corpus release is not a validated 600-repository proposal")

        def read(name, lines=False):
            content = (self.release / name).read_bytes()
            expected = manifest["release_files"][name]
            if (
                hashlib.sha256(content).hexdigest() != expected["sha256"]
                or len(content) != expected["bytes"]
            ):
                raise ValueError("Corpus release integrity failed: " + name)
            return (
                [json.loads(line) for line in content.splitlines() if line]
                if lines
                else json.loads(content)
            )

        rows = read("inventory.jsonl", True)
        labels = read("labels.proposed.jsonl", True)
        registry = read("registry.proposed.json")
        inventory = {r["repository_id"]: r for r in rows}
        proposals = {r["repository_id"]: r for r in labels}
        if len(rows) != 600 or len(inventory) != 600 or set(inventory) != set(proposals):
            raise ValueError("Corpus inventory/proposal identity mismatch")
        counts = Counter(r["sampling_domain"] for r in rows)
        if len(counts) != 10 or set(counts.values()) != {60}:
            raise ValueError("Corpus domain balance failed")
        self.manifest, self.inventory, self.proposals, self.registry = (
            manifest,
            inventory,
            proposals,
            registry,
        )
        self._manifest_hash = manifest_hash

    def records(self, workspace):
        self.load()
        return (
            self.store.read(workspace)
            .get("reference_reviews", {})
            .get(self.manifest["release_id"], {})
        )

    def drafts(self, workspace):
        self.load()
        return (
            self.store.read(workspace)
            .get("reference_drafts", {})
            .get(self.manifest["release_id"], {})
        )

    def _draft_view(self, draft, review, rid, pilot=None, registry_context=None):
        if draft is None:
            return None
        reasons = []
        base_context = self.registry_adapter().view({}, 0)["registry_context"]
        if (
            registry_context is not None
            and (draft.get("registry_context") or base_context) != registry_context
        ):
            reasons.append("The reference vocabulary changed")
        if draft["base_review_revision"] != (review["revision"] if review else 0):
            reasons.append("A newer final review exists")
        if (
            draft["manifest_sha256"] != self._manifest_hash
            or draft["proposal_sha256"] != digest(self.proposals[rid])
            or draft["commit"] != self.inventory[rid]["commit"]
        ):
            reasons.append("The source or proposal context changed")
        if draft.get("annotation_pilot_sha256"):
            pilot = pilot if pilot is not None else self.annotation_pilot()
            if (
                pilot["state"] != "READY"
                or pilot.get("sidecar_manifest_sha256") != draft["annotation_pilot_sha256"]
            ):
                reasons.append("The annotation comparison changed")
        return {**draft, "stale": bool(reasons), "stale_reasons": reasons}

    def draft(self, workspace, rid):
        self.dossier(rid)
        state = self.store.read(workspace)
        release = self.manifest["release_id"]
        return self._draft_view(
            state.get("reference_drafts", {}).get(release, {}).get(str(rid)),
            state.get("reference_reviews", {}).get(release, {}).get(str(rid)),
            rid,
            registry_context=self.registry_adapter().view(state)["registry_context"],
        )

    def save_draft(self, workspace, rid, value, actor):
        record = self.dossier(rid)
        if (
            value["release_id"] != self.manifest["release_id"]
            or value["manifest_sha256"] != self._manifest_hash
        ):
            raise ValueError("Release changed; reload this repository before saving a draft")
        labels = value["label_ids"]
        adapter = self.registry_adapter()
        vocabulary = adapter.check(self.store.read(workspace), value.get("registry_context"))
        registry = {c["id"]: c for c in vocabulary["registry"]}
        if len(set(labels)) != len(labels) or any(
            label not in registry or registry[label]["kind"] == "DOMAIN"
            for label in [*labels, *value["additional_evidence"]]
        ):
            raise ValueError("Choose distinct known Projects, Topics or Tags for this draft")
        paths = {record["readme"]["path"]}
        for label in self.proposals[rid]["labels"]:
            if label["id"] in labels:
                paths.update(
                    e["path"]
                    for e in label.get("evidence", [])
                    if e.get("path")
                    and e.get("app_input_channel") not in {"METADATA", "GITHUB_METADATA"}
                )
        paths.update(e["path"] for e in value["additional_evidence"].values() if e["path"])
        for path in paths:
            self.source(rid, path)
        binding = value.get("annotation_pilot_sha256")
        if binding:
            pilot = self.annotation_pilot()
            if (
                pilot["state"] != "READY"
                or pilot.get("sidecar_manifest_sha256") != binding
                or str(rid) not in pilot.get("records", {})
            ):
                raise ValueError("Annotation pilot changed; reload before saving its suggestions")
        from datetime import UTC, datetime

        def write(state):
            current = adapter.check(state, value.get("registry_context"))
            release = self.manifest["release_id"]
            review = state.get("reference_reviews", {}).get(release, {}).get(str(rid))
            drafts = state.setdefault("reference_drafts", {}).setdefault(release, {})
            old = drafts.get(str(rid))
            if (review["revision"] if review else 0) != value["base_review_revision"]:
                raise CorpusConflict(
                    "A newer review was saved; compare it before saving this draft",
                    "CORPUS_REVIEW_CONFLICT",
                    review,
                    old,
                )
            if (old["revision"] if old else 0) != value["expected_revision"]:
                raise CorpusConflict(
                    "Another draft was saved; reload or compare it before making changes",
                    "CORPUS_DRAFT_CONFLICT",
                    review,
                    old,
                )
            saved = {
                key: value[key]
                for key in (
                    "purpose",
                    "label_ids",
                    "dimensions",
                    "notes",
                    "additional_evidence",
                    "status",
                )
            } | {
                "repository_id": rid,
                "release_id": release,
                "manifest_sha256": self._manifest_hash,
                "commit": record["commit"],
                "proposal_sha256": digest(self.proposals[rid]),
                "annotation_pilot_sha256": binding,
                "actor_id": actor,
                "base_review_revision": value["base_review_revision"],
                "revision": value["expected_revision"] + 1,
                "saved_at_utc": datetime.now(UTC).isoformat(),
                "kind": "INCOMPLETE_DRAFT",
                "registry_context": current["registry_context"],
            }
            drafts[str(rid)] = saved
            return self._draft_view(
                saved, review, rid, registry_context=current["registry_context"]
            )

        return self.store.mutate(workspace, write)

    def open(self, workspace):
        self.load()
        reference = {
            "name": "Public - Ground Truth",
            "release_id": self.manifest["release_id"],
            "manifest_sha256": self._manifest_hash,
        }
        if self.store.read(workspace).get("reference_dataset") != reference:
            self.store.mutate(workspace, lambda state: state.update(reference_dataset=reference))
        return self.summary(workspace)

    def summary(self, workspace):
        reviews = self.records(workspace)
        drafts = self.drafts(workspace)
        vocabulary = self.registry_view(workspace)
        counts = Counter()
        reviewed_counts = Counter()
        for review in reviews.values():
            reviewed_counts.update(
                set(review["label_ids"]) | set(review.get("derived_domains", []))
            )
        for proposal in self.proposals.values():
            counts.update(
                {
                    label["id"]
                    for label in proposal["labels"]
                    if label.get("decision", "SUPPORTED") == "SUPPORTED"
                }
            )
            counts.update(set(proposal.get("derived_domains", [])))
        return {
            "name": "Public - Ground Truth",
            "release_id": self.manifest["release_id"],
            "manifest_sha256": self._manifest_hash,
            "total": len(self.inventory),
            "status": self.manifest["status"],
            "domains": dict(Counter(r["sampling_domain"] for r in self.inventory.values())),
            "registry": [
                {
                    **item,
                    "repository_count": counts[item["id"]],
                    "reviewed_repository_count": reviewed_counts[item["id"]],
                }
                for item in vocabulary["registry"]
            ],
            "registry_context": vocabulary["registry_context"],
            "registry_extension_count": vocabulary["extension_count"],
            "human_confirmed": sum(r["status"] == "HUMAN_CONFIRMED" for r in reviews.values()),
            "reviewed": len(reviews),
            "drafts": len(drafts),
            "proposed": len(self.inventory) - len(reviews),
            "persistence": "Versioned local corpus files + owner-scoped local SQLite reviews",
            "annotation_pilot": self.annotation_pilot_summary(reviews),
        }

    def search(
        self,
        workspace,
        q="",
        domain="",
        concept="",
        status="",
        offset=0,
        limit=25,
        assigned_domain="",
        concept_ids=(),
        label_basis="proposals",
        annotation_scope="all",
    ):
        reviews = self.records(workspace)
        drafts = self.drafts(workspace)
        registry = {c["id"]: c for c in self.registry_view(workspace)["registry"]}
        if annotation_scope not in {"all", "pilot", "initial_queue"}:
            raise ValueError("Choose all, pilot or initial_queue for the annotation scope")
        pilot_ids = None
        if annotation_scope != "all":
            pilot = self.annotation_pilot()
            if pilot["state"] != "READY":
                raise ValueError(
                    "Independent A/B annotations are unavailable. "
                    "Choose all repositories or restore the validated annotation pilot."
                )
            pilot_ids = {
                row["repository_id"]
                for row in pilot["records"].values()
                if annotation_scope == "pilot" or row.get("audit_selection")
            }
        if len(set(concept_ids)) != len(concept_ids) or any(
            cid not in registry or registry[cid]["kind"] == "DOMAIN" for cid in concept_ids
        ):
            raise ValueError("Choose distinct known Project, Topic or Tag filter IDs")
        grouped = {}
        for cid in concept_ids:
            grouped.setdefault(registry[cid]["kind"], set()).add(cid)
        rows = []
        for rid, item in self.inventory.items():
            if pilot_ids is not None and rid not in pilot_ids:
                continue
            proposal = self.proposals[rid]
            review = reviews.get(str(rid))
            positive = (
                (set(review["label_ids"]) if review else set())
                if label_basis == "reviewed"
                else {
                    label["id"]
                    for label in proposal["labels"]
                    if label.get("decision", "SUPPORTED") == "SUPPORTED"
                }
            )
            domains = (
                (review.get("derived_domains", []) if review else [])
                if label_basis == "reviewed"
                else proposal.get("derived_domains", [])
            )
            if domain and item["sampling_domain"] != domain:
                continue
            if assigned_domain and assigned_domain not in domains:
                continue
            if (concept and concept not in positive) or any(
                not (positive & ids) for ids in grouped.values()
            ):
                continue
            review_status = (
                review["status"]
                if review
                else ("DISPUTED" if proposal.get("status") == "DISPUTED" else "PROPOSED")
            )
            if status and review_status != status:
                continue
            if (
                q.casefold()
                not in (
                    item["full_name"]
                    + " "
                    + (proposal.get("purpose") or "")
                    + " "
                    + (item.get("description") or "")
                ).casefold()
            ):
                continue
            rows.append(
                {
                    **item,
                    "purpose": proposal.get("purpose"),
                    "review_status": review_status,
                    "has_draft": str(rid) in drafts,
                    "draft_revision": drafts.get(str(rid), {}).get("revision", 0),
                    "derived_domains": domains,
                    "labels": (
                        [
                            {
                                "id": cid,
                                "name": registry[cid]["name"],
                                "kind": registry[cid]["kind"],
                            }
                            for cid in sorted(positive)
                        ]
                        if label_basis == "reviewed"
                        else [
                            {
                                "id": label_item["id"],
                                "name": label_item["name"],
                                "kind": label_item["kind"],
                            }
                            for label_item in merged_labels(proposal)
                            if label_item.get("decision", "SUPPORTED") == "SUPPORTED"
                        ]
                    ),
                }
            )
        rows.sort(key=lambda r: (r["full_name"].casefold(), r["repository_id"]))
        return {
            "items": rows[offset : offset + limit],
            "total": len(rows),
            "offset": offset,
            "limit": limit,
            "label_basis": label_basis,
            "annotation_scope": annotation_scope,
        }

    def dossier(self, rid):
        self.load()
        item = self.inventory.get(rid)
        if not item:
            raise KeyError("Repository not in this release")
        path = (self.root / item["dossier_path"]).resolve()
        allowed = (self.release.parent / "shards").resolve()
        if not path.is_relative_to(allowed):
            raise ValueError("Corpus dossier path rejected")
        raw = path.read_bytes()
        expected = self.manifest["sources_and_dossiers_sha256"].get(
            str(path.relative_to(self.root))
        )
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError("Corpus dossier integrity failed")
        record = json.loads(raw)
        if (
            record["numeric_id"] != rid
            or record["commit"] != item["commit"]
            or record.get("private") is not False
        ):
            raise ValueError("Corpus dossier identity failed")
        return record

    def neighbors(self, workspace, rid, **filters):
        """Seek by immutable identity even when a save removes the current status match."""
        self.load()
        if rid not in self.inventory:
            raise KeyError("Repository not in this release")
        anchor = (self.inventory[rid]["full_name"].casefold(), rid)
        rows = self.search(workspace, limit=len(self.inventory), **filters)["items"]
        before, after = None, None
        for index, row in enumerate(rows):
            key = (row["full_name"].casefold(), row["repository_id"])
            if key < anchor:
                before = (index, row)
            elif key > anchor and after is None:
                after = (index, row)
        return {
            "previous": before[1] if before else None,
            "previous_index": before[0] if before else None,
            "next": after[1] if after else None,
            "next_index": after[0] if after else None,
            "total": len(rows),
        }

    def source(self, rid, path):
        record = self.dossier(rid)
        if path == "@github-metadata.json":
            metadata = self.metadata_source(rid)
            if metadata is None:
                raise KeyError("Pinned metadata is not available for this pilot repository")
            return metadata
        file = next(
            (
                f
                for f in [record["readme"], *record.get("supporting_files", [])]
                if f["path"] == path
            ),
            None,
        )
        if not file:
            raise KeyError("Source is not in this dossier")
        local = (self.root / file["local_path"]).resolve()
        roots = [
            self.root / "docs/validation/private" / name / "sources"
            for name in ("corpus-600", "corpus-600-v2")
        ]
        if not any(local.is_relative_to(r.resolve()) for r in roots):
            raise ValueError("Corpus source path rejected")
        raw = local.read_bytes()
        if len(raw) != file["bytes"] or hashlib.sha256(raw).hexdigest() != file["sha256"]:
            raise ValueError("Corpus source integrity failed")
        return {
            "path": file["path"],
            "sha256": file["sha256"],
            "commit": record["commit"],
            "text": raw.decode("utf-8", errors="replace"),
            "role": file["role"],
        }

    def detail(self, workspace, rid):
        record = self.dossier(rid)
        state = self.store.read(workspace)
        release = self.manifest["release_id"]
        review = state.get("reference_reviews", {}).get(release, {}).get(str(rid))
        vocabulary = self.registry_adapter().view(state)
        pilot = self.annotation_pilot()
        metadata = self.metadata_source(rid, pilot)
        return {
            "inventory": self.inventory[rid],
            "proposal": {**self.proposals[rid], "labels": merged_labels(self.proposals[rid])},
            "review": review,
            "draft": self._draft_view(
                state.get("reference_drafts", {}).get(release, {}).get(str(rid)),
                review,
                rid,
                pilot,
                vocabulary["registry_context"],
            ),
            "eligibility": record.get(
                "eligibility_v2",
                record.get(
                    "eligibility", record.get("v2_eligibility", record.get("eligibility_audit"))
                ),
            ),
            "files": [
                {k: f[k] for k in ("path", "sha256", "bytes", "role")}
                for f in [record["readme"], *record.get("supporting_files", [])]
            ]
            + ([{k: metadata[k] for k in ("path", "sha256", "bytes", "role")}] if metadata else []),
            "read_coverage": record.get("agent_read_coverage"),
            "release_id": self.manifest["release_id"],
            "manifest_sha256": self._manifest_hash,
            "registry_context": vocabulary["registry_context"],
            "registry": vocabulary["registry"],
            "review_registry_context": (review or {}).get("registry_context")
            or self.registry_adapter().view(state, 0)["registry_context"],
            "annotation_pilot": {
                "state": pilot["state"],
                "sidecar_manifest_sha256": pilot.get("sidecar_manifest_sha256"),
                "record": pilot.get("records", {}).get(str(rid)),
            },
        }

    def save_review(self, workspace, rid, value, actor):
        record = self.dossier(rid)
        # A review can never bind a locally modified source snapshot.
        paths = {record["readme"]["path"]}
        for label in self.proposals[rid]["labels"]:
            if label["id"] in value["label_ids"]:
                paths.update(
                    e["path"]
                    for e in label.get("evidence", [])
                    if e.get("path")
                    and e.get("app_input_channel") not in {"METADATA", "GITHUB_METADATA"}
                )
        for path in paths:
            self.source(rid, path)
        if (
            value["release_id"] != self.manifest["release_id"]
            or value["manifest_sha256"] != self._manifest_hash
        ):
            raise ValueError("Release changed; reload this repository before saving")
        labels = value["label_ids"]
        adapter = self.registry_adapter()
        vocabulary = adapter.check(self.store.read(workspace), value.get("registry_context"))
        registry = {c["id"]: c for c in vocabulary["registry"]}
        if len(set(labels)) != len(labels) or any(
            label_item not in registry or registry[label_item]["kind"] == "DOMAIN"
            for label_item in labels
        ):
            raise ValueError(
                "Choose distinct known Projects, Topics or Tags. Domains derive from Projects."
            )
        purpose = value["purpose"].strip()
        annotation_binding = value.get("annotation_pilot_sha256")
        if annotation_binding:
            pilot = self.annotation_pilot()
            if (
                pilot["state"] != "READY"
                or pilot.get("sidecar_manifest_sha256") != annotation_binding
                or str(rid) not in pilot.get("records", {})
            ):
                raise ValueError("Annotation pilot changed; reload before staging its suggestions")
        if value["status"] == "HUMAN_CONFIRMED" and (
            not purpose or not all(value["dimensions"].values())
        ):
            raise ValueError("Confirmation needs a purpose and review of Projects, Topics and Tags")
        original = {
            label_item["id"]: label_item
            for label_item in self.proposals[rid]["labels"]
            if label_item.get("decision", "SUPPORTED") == "SUPPORTED"
        }
        additions = set(labels) - set(original)
        supplied = value["additional_evidence"]
        for label in additions:
            evidence = supplied.get(label)
            if not evidence or not evidence["quote"].strip():
                raise ValueError("Add an exact source quote for each newly added label")
            source = self.source(rid, evidence["path"])
            if evidence["quote"] not in source["text"]:
                raise ValueError("Added-label evidence must match saved source text exactly")
        from datetime import UTC, datetime

        def write(state):
            current = adapter.check(state, value.get("registry_context"))
            reviews = state.setdefault("reference_reviews", {}).setdefault(
                self.manifest["release_id"], {}
            )
            old = reviews.get(str(rid))
            drafts = state.get("reference_drafts", {}).get(self.manifest["release_id"], {})
            draft = drafts.get(str(rid))
            if (old["revision"] if old else 0) != value["expected_revision"]:
                raise CorpusConflict(
                    "Another review was saved; reload before making changes",
                    "CORPUS_REVIEW_CONFLICT",
                    old,
                    draft,
                )
            expected_draft = value.get("expected_draft_revision")
            if expected_draft is not None and expected_draft != (draft["revision"] if draft else 0):
                raise CorpusConflict(
                    "Another draft was saved; compare it before confirming this review",
                    "CORPUS_DRAFT_CONFLICT",
                    old,
                    draft,
                )
            saved = {
                "repository_id": rid,
                "release_id": self.manifest["release_id"],
                "manifest_sha256": self._manifest_hash,
                "commit": record["commit"],
                "proposal_sha256": digest(self.proposals[rid]),
                "annotation_pilot_sha256": annotation_binding,
                "registry_context": current["registry_context"],
                "actor_id": actor,
                "purpose": purpose,
                "status": value["status"],
                "label_ids": labels,
                "derived_domains": sorted(
                    {
                        registry[label]["domain"]
                        for label in labels
                        if registry[label]["kind"] == "PROJECT" and registry[label].get("domain")
                    }
                ),
                "dimensions": value["dimensions"],
                "additional_evidence": {
                    label_item: supplied[label_item] for label_item in additions
                },
                "notes": value["notes"].strip(),
                "revision": value["expected_revision"] + 1,
                "reviewed_at_utc": datetime.now(UTC).isoformat(),
                "unlisted_labels": "UNKNOWN_NOT_NEGATIVE",
                "history": (
                    old.get("history", []) + [{k: v for k, v in old.items() if k != "history"}]
                )
                if old
                else [],
            }
            reviews[str(rid)] = saved
            # Only a client that observed this exact draft revision may consume it.
            # Older clients without a draft fence leave concurrent buffers intact.
            if draft and expected_draft == draft["revision"]:
                drafts.pop(str(rid))
            state["reference_dataset"] = {
                "name": "Public - Ground Truth",
                "release_id": self.manifest["release_id"],
                "manifest_sha256": self._manifest_hash,
            }
            return saved

        return self.store.mutate(workspace, write)

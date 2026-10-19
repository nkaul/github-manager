"""Append-only, owner-scoped reference vocabulary; never edits the source release."""

import copy
import hashlib
import json
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.demo.domain import normalize
from app.demo.store import identifier


class RegistryContext(BaseModel):
    model_config = ConfigDict(extra="forbid")
    revision: int = Field(ge=0)
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")


class RegistryConceptInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    kind: Literal["DOMAIN", "PROJECT", "TOPIC", "TAG"]
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=1000)
    aliases: list[str] = Field(default_factory=list, max_length=12)
    domain: str | None = Field(default=None, max_length=200)
    registry_context: RegistryContext


class RegistryConflict(ValueError):
    def __init__(self, message, registry, *, conflicts=None, code="CORPUS_REGISTRY_CONFLICT"):
        super().__init__(message)
        self.registry, self.conflicts, self.code = registry, conflicts or [], code


class CorpusRegistry:
    def __init__(self, base, manifest_sha256, release_id):
        self.base, self.manifest_sha256, self.release_id = base, manifest_sha256, release_id

    def view(self, state, revision=None):
        saved = state.get("reference_registries", {}).get(self.release_id, {})
        if saved and saved.get("base_manifest_sha256") != self.manifest_sha256:
            raise ValueError("Reference vocabulary belongs to a different source release")
        revision = saved.get("revision", 0) if revision is None else revision
        if revision == 0:
            extensions = {}
        else:
            version = saved.get("versions", {}).get(str(revision))
            if version is None:
                raise ValueError("Reference vocabulary version is unavailable")
            extensions = version["concepts"]
        context = {
            "revision": revision,
            "sha256": hashlib.sha256(
                json.dumps(
                    {"base_manifest_sha256": self.manifest_sha256, "extensions": extensions},
                    sort_keys=True,
                    ensure_ascii=False,
                ).encode()
            ).hexdigest(),
        }
        return {
            "release_id": self.release_id,
            "manifest_sha256": self.manifest_sha256,
            "registry_context": context,
            "registry": [*self.base.values(), *extensions.values()],
            "extension_count": len(extensions),
        }

    def check(self, state, context):
        current = self.view(state)
        expected = context or self.view(state, 0)["registry_context"]
        if expected != current["registry_context"]:
            raise RegistryConflict(
                "Reference vocabulary changed. "
                "Refresh the vocabulary and review your edits before saving.",
                current,
            )
        return current

    def create(self, state, value, actor):
        current = self.check(state, value["registry_context"])
        terms = [("name", value["name"]), *(("aliases", a) for a in value["aliases"])]
        conflicts, seen = [], set()
        for field, term in terms:
            key = normalize(term)
            if not key or len(term) > 100:
                raise ValueError("Names and aliases need 1–100 meaningful characters")
            if key in seen:
                conflicts.append(
                    {
                        "field": field,
                        "term": term,
                        "message": f"“{term}” repeats the name or another alias.",
                    }
                )
            seen.add(key)
            for concept in current["registry"]:
                if concept["kind"] != value["kind"]:
                    continue
                for existing_field, existing_term in [
                    ("name", concept["name"]),
                    *(("alias", a) for a in concept.get("aliases", [])),
                ]:
                    if normalize(existing_term) == key:
                        conflicts.append(
                            {
                                "field": field,
                                "term": term,
                                "kind": value["kind"],
                                "existing": concept,
                                "existing_field": existing_field,
                                "message": (
                                    f"“{term}” is already reserved as {existing_field} "
                                    f"“{existing_term}” on {concept['kind'].lower()} "
                                    f"“{concept['name']}”."
                                ),
                            }
                        )
        if conflicts:
            raise RegistryConflict(
                conflicts[0]["message"],
                current,
                conflicts=conflicts,
                code="CORPUS_REGISTRY_NAME_CONFLICT",
            )
        concepts = {c["id"]: c for c in current["registry"]}
        if value["kind"] == "PROJECT":
            parent = concepts.get(value["domain"])
            if not parent or parent["kind"] != "DOMAIN" or parent.get("active") is False:
                raise ValueError("Choose an active Domain for the new Project")
        elif value["domain"]:
            raise ValueError("Only Projects have a parent Domain")
        if current["extension_count"] >= 200:
            raise ValueError("This local reference extension supports up to 200 new concepts")
        item = {key: value[key] for key in ("kind", "name", "description", "aliases", "domain")} | {
            "id": "reference:" + identifier(),
            "active": True,
            "origin": "HUMAN_REFERENCE_EXTENSION",
            "created_at": datetime.now(UTC).isoformat(),
            "created_by": actor,
        }
        saved = state.setdefault("reference_registries", {}).setdefault(
            self.release_id,
            {
                "base_manifest_sha256": self.manifest_sha256,
                "revision": 0,
                "versions": {},
            },
        )
        extensions = {c["id"]: c for c in current["registry"] if c["id"] not in self.base}
        extensions[item["id"]] = item
        revision = saved["revision"] + 1
        saved["versions"][str(revision)] = {
            "concepts": copy.deepcopy(extensions),
            "created_at": item["created_at"],
        }
        saved["revision"] = revision
        return {"concept": item, **self.view(state)}

    def export(self, state):
        current = self.view(state)
        saved = state.get("reference_registries", {}).get(self.release_id, {})
        return {
            **current,
            "versions": [
                {
                    "registry_context": self.view(state, revision)["registry_context"],
                    "extensions": list(
                        saved.get("versions", {})
                        .get(str(revision), {})
                        .get("concepts", {})
                        .values()
                    ),
                }
                for revision in range(saved.get("revision", 0) + 1)
            ],
            "evaluation_note": (
                "Human-created concepts were unavailable to the original fixed-registry readers. "
                "Compare matching registry versions; do not retroactively score registry gaps "
                "as missed known labels. Legacy records without a registry context use version 0."
            ),
        }

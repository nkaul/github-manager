"""Explicit deterministic providers for tests only; never imported by the product entrypoint."""

import base64
from types import SimpleNamespace

from app.demo import domain
from app.pretest.ai.schemas import TaxonomyDraft

USER = {"id": 9009, "login": "phase09-fixture", "name": "Demo Test Fixture"}


class Adapter:
    def authorization_url(self, state, verifier):
        return "/api/v1/auth/github/callback?code=fixture-only&state=" + state

    async def exchange(self, code, verifier):
        assert code == "fixture-only" and verifier
        return {"access_token": "test-only-token", "scope": "repo,read:user"}

    async def identity(self, token):
        return USER

    async def inventory(self, token):
        return {
            "identity": USER,
            "coverage": [
                {
                    "source": "FIXTURE",
                    "status": "FIXTURE",
                    "note": "Deterministic test inventory, not live GitHub evidence",
                }
            ],
            "repos": [
                {
                    "id": 10,
                    "full_name": "fixture/api",
                    "html_url": "https://github.com/fixture/api",
                    "private": False,
                    "language": "Python",
                    "default_branch": "main",
                    "eligible": True,
                    "favorite": True,
                    "sources": ["OWNER", "STAR"],
                },
                {
                    "id": 11,
                    "full_name": "fixture/private",
                    "html_url": "https://github.com/fixture/private",
                    "private": True,
                    "language": "Python",
                    "default_branch": "main",
                    "eligible": True,
                    "favorite": False,
                    "sources": ["OWNER"],
                },
            ],
        }

    async def request(self, token, path, **kwargs):
        if path == "/graphql":
            raise ValueError("Activity fixture provided separately")
        if path == "/repositories/10":
            return {
                "id": 10,
                "private": False,
                "full_name": "fixture/api",
                "description": "Orion API backend",
                "topics": ["api"],
                "language": "Python",
            }, None
        if path.endswith("/readme"):
            return {
                "encoding": "base64",
                "size": 44,
                "sha": "fixture-sha",
                "content": base64.b64encode(
                    b"# Orion API\nAPI backend for the Orion initiative."
                ).decode(),
            }, None
        raise ValueError("Unexpected fixture request")


class Provider:
    calls = 0
    settings = SimpleNamespace(
        openai_taxonomy_model="fixture-taxonomy",
        openai_classification_model="fixture-classification",
    )

    def __init__(self, mode, authorized):
        self.authorized = authorized

    def close(self):
        pass

    def invoke(self, model, task, schema, system, evidence, validator, **kwargs):
        assert self.authorized(), "Fixture workspace fence changed"
        type(self).calls += 1
        assert evidence["private"] is False
        if schema is TaxonomyDraft:
            keys = [r["repo_id"] for r in evidence["collection"]]
            proposals = []
            for kind, name, parent in [
                ("DOMAIN", "Applications", None),
                ("PROJECT", "Orion", "Applications"),
                ("TOPIC", "Web APIs", None),
                ("TAG", "python", None),
            ]:
                proposals.append(
                    {
                        "kind": kind,
                        "name": name,
                        "description": "Test fixture: " + name,
                        "aliases": [],
                        "parent_domain": parent,
                        "supporting_repo_ids": keys,
                    }
                )
            result = {
                "proposals": proposals,
                "notes": "DETERMINISTIC FIXTURE; not live model output",
            }
        else:
            candidates = evidence["candidates"]
            chosen = next((c for c in candidates if c["kind"] == "PROJECT"), candidates[0])
            result = {
                "status": "CLASSIFIED",
                "assignments": [
                    {
                        "kind": chosen["kind"],
                        "concept_id": chosen["id"],
                        "confidence": 0.9,
                        "evidence_ids": [evidence["evidence"][0]["id"]],
                        "reason": "Test fixture evidence",
                    }
                ],
                "summary": "Deterministic test fixture",
            }
        parsed = validator(schema.model_validate(result))
        return {
            "status": "PASS",
            "evidence": "FIXTURE",
            "result": parsed.model_dump(),
            "returned_model": model,
            "seconds": 0.01,
            "usage": {"input_tokens": 0, "output_tokens": 0},
        }


def concept(store, workspace, kind, name, parent=None, aliases=None):
    return store.mutate(
        workspace,
        lambda s: domain.create_concept(
            s,
            {
                "kind": kind,
                "name": name,
                "description": name,
                "domain": parent,
                "aliases": aliases or [],
            },
        ),
    )

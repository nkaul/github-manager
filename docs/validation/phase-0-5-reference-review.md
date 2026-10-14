# Phase 0.5 reference review

Status: **APPROVED by the user, October 11, 2026.** Approval covers the public expected concept sets and registry semantics for the frozen corpus below. Taxonomy drafts and extraction usefulness require separate review.

Frozen corpus hash: `7c9d88ed1a2e31c1b5638e8ad75e0aaf892fe18b16a3d7e5520a0ddf4998693c`.

Public labels are implementer-proposed minimum expected labels, not model-generated truth. Review evidence and correct the expected sets before a quality PASS. Synthetic cases have authored expected outcomes. Models never see labels. Related repos are kept in the same split. No project is expected for public libraries solely because they share an owner/framework.

| Case | Split/source | Approved minimum expected concepts |
|---|---|---|
| [fastapi/fastapi](https://github.com/fastapi/fastapi) | heldout / PUBLIC_GITHUB | Web APIs, python |
| [Kludex/starlette](https://github.com/Kludex/starlette) | heldout / PUBLIC_GITHUB | Web APIs, python |
| [encode/httpx](https://github.com/encode/httpx) | heldout / PUBLIC_GITHUB | HTTP Clients, python |
| [pydantic/pydantic](https://github.com/pydantic/pydantic) | heldout / PUBLIC_GITHUB | Data Validation, python |
| [astral-sh/uv](https://github.com/astral-sh/uv) | dev / PUBLIC_GITHUB | Package Management, python, rust |
| [astral-sh/ruff](https://github.com/astral-sh/ruff) | dev / PUBLIC_GITHUB | Code Linting, python, rust |
| [pallets/flask](https://github.com/pallets/flask) | heldout / PUBLIC_GITHUB | Web APIs, python |
| [pallets/click](https://github.com/pallets/click) | heldout / PUBLIC_GITHUB | Command Line Interfaces, python |
| [pallets/jinja](https://github.com/pallets/jinja) | heldout / PUBLIC_GITHUB | Templating, python |
| [pytest-dev/pytest](https://github.com/pytest-dev/pytest) | heldout / PUBLIC_GITHUB | Software Testing, python |
| synthetic/orion-api | heldout / SYNTHETIC | Orion Clinical Platform, Web APIs, fastapi, python |
| synthetic/orion-ui | heldout / SYNTHETIC | Orion Clinical Platform, Visualization, react, typescript |
| synthetic/orion-booking | heldout / SYNTHETIC | Orion Clinical Platform, Scheduling, python |
| synthetic/orion-audit | heldout / SYNTHETIC | Orion Clinical Platform, Compliance Audit Initiative, Audit Logging, python |
| synthetic/helios-ingest | heldout / SYNTHETIC | Helios Grid Initiative, Telemetry, mqtt, python |
| synthetic/helios-forecast | heldout / SYNTHETIC | Helios Grid Initiative, Forecasting, pandas, python |
| synthetic/helios-dashboard | heldout / SYNTHETIC | Helios Grid Initiative, Telemetry, Visualization, typescript, react |
| synthetic/helios-audit | heldout / SYNTHETIC | Helios Grid Initiative, Compliance Audit Initiative, Audit Logging, python |
| synthetic/unknown-empty | heldout / SYNTHETIC | NO_MATCH |
| synthetic/unknown-fork | heldout / SYNTHETIC | NO_MATCH |
| synthetic/negated-api | heldout / SYNTHETIC | HTTP Clients, python |
| synthetic/metadata-only | heldout / SYNTHETIC | Data Validation, python |
| synthetic/atlas-samples | dev / SYNTHETIC | Atlas Laboratory Suite, Sample Tracking, postgresql, python |
| synthetic/atlas-api | dev / SYNTHETIC | Atlas Laboratory Suite, Web APIs, Sample Tracking, fastapi, python |
| synthetic/atlas-audit | dev / SYNTHETIC | Atlas Laboratory Suite, Audit Logging, python |
| synthetic/meridian-ocean | dev / SYNTHETIC | Meridian Ocean Research, Telemetry, python |
| synthetic/meridian-charts | dev / SYNTHETIC | Meridian Ocean Research, Visualization, react, typescript |
| synthetic/install-noise | dev / SYNTHETIC | Command Line Interfaces, python |
| synthetic/injection | dev / SYNTHETIC | HTTP Clients, python, Software Testing |
| synthetic/spanish | dev / SYNTHETIC | Data Validation, python |

## Registry semantics

Projects represent initiatives; topics describe capabilities; tags describe technologies. Domains derive through project membership. One repository can have multiple projects. Orion/Helios/Atlas/Meridian are authored synthetic initiatives. The other project entries are distractors for lexical retrieval. Negated-api names Helios/Orion but explicitly excludes membership.

Public expected sets and registry semantics are approved. These are minimum expected sets; extra model labels need independent adjudication before precision is treated as exhaustive quality truth. Preserve original scores and record amendments separately. Pending review: rate actual taxonomy drafts using relevance, support, hierarchy, alias/distinctness and logical grouping (1–5 each). An algorithm/model cannot approve its own reference labels or assign a human rubric score.

Subsequent adjudication: the user requires **primary labels only**. FastAPI’s extra Data Validation topic and fastapi tag count as secondary-label errors. No reference labels or original scores were changed. Taxonomy/extraction received qualitative “looks ok” feedback; no numeric ratings were supplied.

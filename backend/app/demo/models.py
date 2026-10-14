from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Kind = Literal["DOMAIN", "PROJECT", "TOPIC", "TAG"]


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ConceptInput(Strict):
    kind: Kind
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=300)
    aliases: list[str] = Field(default_factory=list, max_length=6)
    domain: str | None = None


class ConceptPatch(Strict):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=300)
    aliases: list[str] | None = Field(default=None, max_length=6)
    domain: str | None = None

    @model_validator(mode="after")
    def non_null_text(self):
        if any(
            getattr(self, name) is None
            for name in self.model_fields_set & {"name", "description", "aliases"}
        ):
            raise ValueError("Name, description and aliases cannot be null")
        return self


class MergeInput(Strict):
    source: str
    target: str


class MappingInput(Strict):
    repo_keys: list[str] = Field(min_length=1, max_length=500)
    concept_ids: list[str] = Field(min_length=1, max_length=12)
    operation: Literal["ADD", "REMOVE"] = "ADD"


class RuleInput(Strict):
    name: str = Field(min_length=1, max_length=100)
    field: Literal["name", "owner", "language", "topic"]
    operator: Literal["equals", "contains"]
    value: str = Field(min_length=1, max_length=100)
    concept_id: str


class RunInput(Strict):
    mode: Literal["EXTRACT", "DISCOVER", "REDISCOVER", "INCREMENTAL", "FULL_CLASSIFICATION"]
    repo_keys: list[str] = Field(default_factory=list, max_length=30)
    ai_mode: Literal["LIVE", "CACHE", "RULES"] = "CACHE"


class RepoScope(Strict):
    view: Literal[
        "my",
        "favorites",
        "latest",
        "uncategorized",
        "all",
        "no_labels",
        "needs_review",
        "no_match",
        "failed",
        "stale",
    ] = "my"
    q: str = Field(default="", max_length=100)
    language: str = Field(default="", max_length=100)
    visibility: Literal["all", "public", "private"] = "all"
    concept: str = Field(default="", max_length=100)
    days: int = Field(default=14, ge=1, le=90)


class RunPreview(Strict):
    mode: Literal["EXTRACT", "DISCOVER", "REDISCOVER", "INCREMENTAL", "FULL_CLASSIFICATION"]
    ai_mode: Literal["LIVE", "CACHE", "RULES"] = "CACHE"
    selection: Literal["AUTO", "MANUAL"] = "AUTO"
    repo_keys: list[str] = Field(default_factory=list, max_length=30)
    count: int = Field(default=10, ge=1, le=30, strict=True)
    scope: RepoScope = Field(default_factory=RepoScope)
    budget_mode: Literal["FIXED", "ADAPTIVE"] = "FIXED"
    budget_usd: float = Field(default=0.25, gt=0, le=5, allow_inf_nan=False)
    reanalyze: bool = False
    reanalysis_reason: str = Field(default="", max_length=200)

    @model_validator(mode="after")
    def explicit_reanalysis(self):
        if self.reanalyze and (
            len(self.reanalysis_reason) < 3 or self.ai_mode != "LIVE" or self.mode == "EXTRACT"
        ):
            raise ValueError(
                "Re-analysis needs Live AI, a model operation and a reason (3–200 characters)"
            )
        return self


class ExecutePlan(Strict):
    plan_id: str = Field(min_length=10, max_length=100)


class SelectionSummary(Strict):
    repo_keys: list[str] = Field(default_factory=list, max_length=500)


class RunPreferences(Strict):
    taxonomy_count: int = Field(default=10, ge=1, le=30)
    classification_count: int = Field(default=10, ge=1, le=30)
    budget_mode: Literal["FIXED", "ADAPTIVE"] = "FIXED"
    budget_usd: float = Field(default=0.25, gt=0, le=5, allow_inf_nan=False)


class PublishInput(Strict):
    draft_id: str
    proposals: list[ConceptInput] = Field(min_length=1, max_length=50)
    expected_revision: int


class RemediateInput(PublishInput):
    action: Literal["REMOVE_ALIAS", "RENAME", "REUSE", "EXCLUDE", "CLEAN_ALIASES"]
    conflict_id: str | None = Field(default=None, max_length=100)


class DraftPatch(Strict):
    proposals: list[ConceptInput] = Field(min_length=1, max_length=50)


class SettingsInput(Strict):
    auto_enabled: bool | None = None
    quiet_seconds: int | None = Field(default=None, ge=0, le=3600, strict=True)
    cooldown_seconds: int | None = Field(default=None, ge=0, le=86400, strict=True)
    auto_window_seconds: int | None = Field(default=None, ge=60, le=86400, strict=True)
    auto_weight_threshold: int | None = Field(default=None, ge=1, le=100, strict=True)
    auto_entity_threshold: int | None = Field(default=None, ge=1, le=100, strict=True)
    auto_project_threshold: int | None = Field(default=None, ge=0, le=100, strict=True)
    auto_change_types: (
        list[Literal["CREATE", "CREATE_PROJECT", "EDIT", "ARCHIVE", "MERGE", "RULE", "EVIDENCE"]]
        | None
    ) = Field(default=None, min_length=1, max_length=7)


class SuggestionBatch(Strict):
    ids: list[str] = Field(min_length=1, max_length=100)
    decision: Literal["accept", "reject"]


class ResetScope(Strict):
    associations: bool = True
    suggestions: bool = True
    drafts: bool = True
    history: bool = True
    feedback: bool = False
    cache: bool = False
    kinds: list[Kind] = Field(default_factory=list, max_length=4)
    rules: bool = False
    restart: Literal["NONE", "RECLASSIFY_EXISTING", "DISCOVER_AND_RECONCILE"] = "NONE"


class ResetExecute(BaseModel):
    # Confirmation MUST NOT be normalized/stripped.
    model_config = ConfigDict(extra="forbid")
    plan_id: str
    confirmation: str

"""In-memory pretest controller; no production persistence or mutation behavior."""


class LocalOrganizationRun:
    def __init__(self, repository_ids, registry, *, manual=None, rejected=None):
        self.pending = set(repository_ids)
        self.registry = registry
        self.manual = manual or {}
        self.rejected = rejected or {}
        self.results = {}
        self.history = ["QUEUED"]

    def start(self):
        if self.history[-1] != "QUEUED":
            raise ValueError("Run already started")
        self.history.append("RUNNING")

    def record(self, repository_id, assignments, *, failed=False):
        if self.history[-1] != "RUNNING" or repository_id not in self.pending:
            raise ValueError("Unexpected, duplicate or terminal repository result")
        manual = set(self.manual.get(repository_id, []))
        rejected = set(self.rejected.get(repository_id, []))
        proposed = set(assignments) - manual - rejected if not failed else set()
        if any(i not in self.registry or self.registry[i]["kind"] == "DOMAIN" for i in proposed):
            raise ValueError("Unknown/direct-domain result cannot be proposed")
        self.results[repository_id] = {
            "USER": sorted(manual),
            "PROPOSED": sorted(proposed),
            "REJECTED": sorted(rejected),
            "failed": failed,
            "domains": sorted(
                {
                    self.registry[i]["domain"]
                    for i in manual | proposed
                    if self.registry[i]["kind"] == "PROJECT"
                }
            ),
        }
        self.pending.remove(repository_id)

    def finish(self):
        if self.history[-1] != "RUNNING" or self.pending:
            raise ValueError("Run cannot finish before every repository outcome is recorded")
        failures = sum(r["failed"] for r in self.results.values())
        self.history.append("PARTIAL_FAILED" if failures else "COMPLETED")
        return {
            "state": self.history[-1],
            "history": self.history.copy(),
            "repos": self.results,
            "counts": {
                "processed_repos": len(self.results),
                "failed_repos": failures,
                "manual_repos": sum(bool(r["USER"]) for r in self.results.values()),
                "proposed_repos": sum(bool(r["PROPOSED"]) for r in self.results.values()),
                "uncategorized_repos": sum(
                    not r["USER"] and not r["PROPOSED"] and not r["failed"]
                    for r in self.results.values()
                ),
            },
            "canonical_published": False,
            "github_mutations": 0,
        }

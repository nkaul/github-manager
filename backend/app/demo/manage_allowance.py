"""Local operator CLI; renew an allowance window or selectively set its limits."""

import argparse
import json

from app.demo.ai import budget_summary
from app.demo.allowance import AllowanceUpdate, RequestAllowance
from app.pretest.ai.settings import AISettings
from app.pretest.ai.storage import Ledger


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["status", "renew", "set"])
    parser.add_argument("--requests", type=int)
    parser.add_argument("--generations", type=int)
    parser.add_argument("--reason")
    parser.add_argument("--expected-revision", type=int)
    args = parser.parse_args()
    settings = AISettings()
    ledger = Ledger(settings.ai_pretest_state_directory, settings.ai_pretest_budget_usd)
    allowance = RequestAllowance(ledger)
    if args.action != "status":
        if not args.reason:
            parser.error("An audit --reason is required")
        value = AllowanceUpdate(
            action="RENEW" if args.action == "renew" else "SET_LIMITS",
            expected_revision=(
                args.expected_revision
                if args.expected_revision is not None
                else allowance.policy()["revision"]
            ),
            requests=args.requests
            if args.requests is not None
            else (20 if args.action == "renew" else None),
            generations=args.generations,
            reason=args.reason,
        )
        allowance.update(value, actor="local-cli")
    print(json.dumps(budget_summary(ledger), indent=2))


if __name__ == "__main__":
    main()

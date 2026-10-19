"""Create local framework configs; no provider calls or uploads."""

import argparse
from pathlib import Path

from runner import HERE, OUT, ROOT, read, save, verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write a separate replay config, preserving the original.")
    args = parser.parse_args()
    verify()
    cases = read(OUT / "reference-snapshot.json")
    settings = {
        "description": "Reviewed-30 saved-output replay: validity assertions and partial-label scores",
        "prompts": ["Replay the exact saved classification for repository {{repository_id}}."],
        "providers": [
            {
                "id": "file://" + str(HERE / "promptfoo_replay.py"),
                "config": {"pythonExecutable": str(ROOT / "backend/.venv/bin/python")},
            }
        ],
        "tests": [
            {
                "description": case["name"],
                "vars": {"repository_id": rid},
                "assert": [
                    {
                        "type": "python",
                        "value": "file://" + str(HERE / "promptfoo_replay.py") + ":get_assert",
                        "threshold": 0,
                    }
                ],
            }
            for rid, case in cases.items()
        ],
        "evaluateOptions": {"maxConcurrency": 1},
        "sharing": False,
    }
    if args.output:
        from app.pretest.ai.storage import private_json
        private_json(args.output, settings)
    else:
        save("promptfoo-config.json", settings)
    print("Saved Promptfoo replay config for", len(cases), "cases; no model provider enabled.")


if __name__ == "__main__":
    main()

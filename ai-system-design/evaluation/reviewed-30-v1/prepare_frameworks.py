"""Create local framework configs; no provider calls or uploads."""

from runner import HERE, OUT, ROOT, read, save, verify


def main():
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
    save("promptfoo-config.json", settings)
    print("Saved Promptfoo replay config for", len(cases), "cases; no model provider enabled.")


if __name__ == "__main__":
    main()

import json

from app.pretest.ai.runner import main

try:
    result = main()
except Exception as error:
    # Settings errors can include input values; never emit their exception text.
    print(json.dumps({"status": "BLOCKED", "error_type": type(error).__name__}))
    result = 2
raise SystemExit(result)

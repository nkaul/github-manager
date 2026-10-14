"""Serve only the packaged full demo, with HTTP ranges for chapter seeking."""

import functools
import importlib.util
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "demo/full-v2"
spec = importlib.util.spec_from_file_location(
    "original_demo_server", ROOT / "demo/tools/serve.py"
)
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)
original.ARTIFACTS = {
    "",
    "player-qa.json",
    "synchronization-qa.json",
    "player-desktop.png",
    "player-phone.png",
    "player-fullscreen.png",
    "preservation-qa.json",
    "historical-coverage.json",
    "README.md",
} | {
    p.name
    for p in OUT.iterdir()
    if p.is_file()
    and p.suffix
    in {".html", ".mp4", ".m4a", ".vtt", ".srt", ".json", ".jpg", ".png", ".md"}
}
server = ThreadingHTTPServer(
    ("127.0.0.1", 8123), functools.partial(original.MediaHandler, directory=str(OUT))
)
print("Full Cedar demo: http://127.0.0.1:8123", flush=True)
try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    server.server_close()

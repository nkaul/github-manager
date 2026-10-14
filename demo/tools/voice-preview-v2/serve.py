"""Serve packaged voice previews only, with media byte-range seeking."""

import functools
import importlib.util
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "demo/voice-preview-v2"
spec = importlib.util.spec_from_file_location(
    "original_demo_server", ROOT / "demo/tools/serve.py"
)
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)
original.ARTIFACTS = {
    "",
    "player-qa.json",
    "comparison-desktop.png",
    "comparison-phone.png",
    "final-protection-1080p.png",
    "final-appearance-1080p.png",
} | {
    p.name
    for p in OUT.iterdir()
    if p.is_file()
    and p.suffix
    in {".html", ".mp4", ".m4a", ".vtt", ".srt", ".json", ".png", ".svg", ".md"}
}
server = ThreadingHTTPServer(
    ("127.0.0.1", 8122), functools.partial(original.MediaHandler, directory=str(OUT))
)
print("Voice comparison: http://127.0.0.1:8122", flush=True)
try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    server.server_close()

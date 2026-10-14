"""Serve only packaged walkthrough artifacts on localhost, with HTTP byte ranges."""

import argparse
import functools
import re
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ARTIFACTS = {
    "", "index.html", "poster.png", "chapters.json", "validation.json", "media-qa.json",
    "github-manager-walkthrough-1080p.mp4", "github-manager-narration.m4a",
    "github-manager-walkthrough.vtt",
}


class MediaHandler(SimpleHTTPRequestHandler):
    byte_range = None

    def send_head(self):
        name = urlsplit(self.path).path.lstrip("/")
        if name not in ARTIFACTS:
            self.send_error(HTTPStatus.NOT_FOUND)
            return None
        self.byte_range = None
        header = self.headers.get("Range")
        if not header:
            return super().send_head()
        target = Path(self.directory) / (name or "index.html")
        if not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return None
        size = target.stat().st_size
        match = re.fullmatch(r"bytes=(\d*)-(\d*)", header)
        if not match or not any(match.groups()):
            self.send_error(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
            return None
        first, last = match.groups()
        start = int(first) if first else max(0, size - int(last))
        end = min(int(last), size - 1) if first and last else size - 1
        if start >= size or end < start:
            self.send_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
            self.send_header("Content-Range", f"bytes */{size}")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return None
        self.send_response(HTTPStatus.PARTIAL_CONTENT)
        self.send_header("Content-Type", self.guess_type(str(target)))
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Accept-Ranges", "bytes")
        self.end_headers()
        stream = target.open("rb")
        stream.seek(start)
        self.byte_range = (start, end)
        return stream

    def end_headers(self):
        if self.byte_range is None:
            self.send_header("Accept-Ranges", "bytes")
        super().end_headers()

    def copyfile(self, source, outputfile):
        try:
            if self.byte_range is None:
                return super().copyfile(source, outputfile)
            remaining = self.byte_range[1] - self.byte_range[0] + 1
            while remaining:
                data = source.read(min(65536, remaining))
                if not data:
                    break
                outputfile.write(data)
                remaining -= len(data)
        except (BrokenPipeError, ConnectionResetError):
            pass  # Seeking cancels an earlier download.


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8120)
    args = parser.parse_args()
    handler = functools.partial(MediaHandler, directory=str(Path(__file__).resolve().parents[1]))
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    print(f"Walkthrough player: http://127.0.0.1:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

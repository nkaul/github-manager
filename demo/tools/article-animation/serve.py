"""Local pilot player; serve only its packaged media, never repository files."""
import argparse
import functools
import importlib.util
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/"demo/article-animation"
spec=importlib.util.spec_from_file_location('prior_media_server',ROOT/'demo/tools/serve.py')
original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
original.ARTIFACTS={'','index.html','overview-1080p.mp4','narration.m4a','poster.png','captions.vtt','captions.srt','chapters.json','timing.json','transcript.md','README.md','media-qa.json','player-qa.json','speech-requests.json'}
parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8124);args=parser.parse_args()
server=ThreadingHTTPServer(('127.0.0.1',args.port),functools.partial(original.MediaHandler,directory=str(OUT)))
print(f'Animated pilot: http://127.0.0.1:{args.port}',flush=True)
try:server.serve_forever()
except KeyboardInterrupt:pass
finally:server.server_close()

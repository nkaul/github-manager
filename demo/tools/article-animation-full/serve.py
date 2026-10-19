"""Serve only the full companion package on localhost, with byte-range seeking."""
import argparse,functools,importlib.util
from http.server import ThreadingHTTPServer
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'demo/article-animation-full'
spec=importlib.util.spec_from_file_location('prior_media_server',ROOT/'demo/tools/serve.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
module.ARTIFACTS={'','index.html'}|{str(p.relative_to(OUT)) for p in OUT.rglob('*') if p.is_file() and p.suffix in {'.html','.mp4','.m4a','.vtt','.srt','.png','.jpg','.json','.md'}}
# Player verification creates these after the preview server starts.
module.ARTIFACTS|={'player-qa.json','player-fullscreen.png','player-desktop.png','player-phone.png','checksums.json',
                  'README.md','validation.md','media-qa.json','sync-qa.json','motion-qa.json'}
p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8125);a=p.parse_args()
s=ThreadingHTTPServer(('127.0.0.1',a.port),functools.partial(module.MediaHandler,directory=str(OUT)))
print(f'Full animated companion: http://127.0.0.1:{a.port}',flush=True)
try:s.serve_forever()
except KeyboardInterrupt:pass
finally:s.server_close()

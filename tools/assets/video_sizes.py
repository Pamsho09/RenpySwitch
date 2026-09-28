"""Record original video dimensions so reduced files keep their layout."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,tempfile,subprocess,argparse
from rpa_audit import index
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('archive',type=Path)
parser.add_argument('output',type=Path)
parser.add_argument('--ffprobe',default='ffprobe')
args=parser.parse_args()
archive=args.archive
entries=index(archive)
def inspect(name):
 with tempfile.TemporaryDirectory() as temp:
  source=Path(temp)/'source.webm'
  with archive.open('rb') as stream,source.open('wb') as out:
   for offset,size,prefix in entries[name]:
    stream.seek(offset);out.write(prefix+stream.read(size-len(prefix)))
  result=json.loads(subprocess.check_output([args.ffprobe,'-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','json',str(source)]))['streams'][0]
  return name,[result['width'],result['height']]
names=sorted(n for n in entries if n.endswith('.webm'))
with ThreadPoolExecutor(max_workers=4) as pool: sizes=dict(pool.map(inspect,names))
output=args.output;output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(sizes,indent=2)+'\n')
print('Original dimensions recorded:',len(sizes))

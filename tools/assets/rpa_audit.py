import argparse, collections, io, json, pickle, pathlib, zlib
class DataOnly(pickle.Unpickler):
    def find_class(self, module, name):
        raise ValueError('Unexpected executable pickle: %s.%s' % (module,name))
def index(path):
    with path.open('rb') as f:
        h=f.read(40)
        if not h.startswith((b'RPA-3.0 ',b'RPA-2.0 ')): raise ValueError(repr(h))
        off=int(h[8:24],16); key=int(h[25:33],16) if h.startswith(b'RPA-3.0 ') else 0; f.seek(off)
        d=DataOnly(io.BytesIO(zlib.decompress(f.read())),encoding='bytes').load()
    return {(n.decode('utf8') if isinstance(n,bytes) else n):[(t[0]^key,t[1]^key,t[2] if len(t)>2 else b'') for t in ts] for n,ts in d.items()}
def extract(path,d,out,extensions):
    with path.open('rb') as f:
        for n,ts in d.items():
            if pathlib.Path(n).suffix.lower() not in extensions: continue
            p=out/n
            if not p.resolve().is_relative_to(out.resolve()): raise ValueError(n)
            p.parent.mkdir(parents=True,exist_ok=True)
            with p.open('wb') as dest:
                for off,size,prefix in ts:
                    if isinstance(prefix,str): prefix=prefix.encode('latin1')
                    f.seek(off); dest.write(prefix); dest.write(f.read(size-len(prefix)))
if __name__=='__main__':
    a=argparse.ArgumentParser(); a.add_argument('archives',nargs='+'); a.add_argument('--out',required=True); a.add_argument('--extract',action='store_true'); args=a.parse_args()
    out=pathlib.Path(args.out); out.mkdir(parents=True,exist_ok=True)
    for archive in args.archives:
        p=pathlib.Path(archive); d=index(p)
        report={'archive':str(p),'count':len(d),'extensions':dict(collections.Counter(pathlib.Path(n).suffix.lower() for n in d)), 'files':{n:sum(t[1] for t in ts) for n,ts in d.items()}}
        (out/(p.stem+'-index.json')).write_text(json.dumps(report,indent=2))
        print(p.name, report['count'],report['extensions'],flush=True)
        if args.extract: extract(p,d,out/p.stem,{'.rpy','.rpyc','.py','.json','.ttf','.otf'})

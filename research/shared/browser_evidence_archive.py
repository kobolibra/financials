"""Lossless storage of actual browser PNG/SVG evidence, never simulated proof.

Per-issuer ZIPs keep repository/API transfer small. Every archive SHA and every
original evidence file SHA are checked; paths cannot escape the proof directory.
"""
from pathlib import Path
import hashlib,io,json,zipfile
class EvidenceReader:
 def __init__(self,root,proof):
  self.root=Path(root).resolve();self.base=Path(proof).resolve().parent;self.base.relative_to(self.root);self.cache={}
 def read(self,name,code):
  file=(self.base/name).resolve();file.relative_to(self.base)
  if file.is_file():return file.read_bytes()
  index=json.loads((self.base/'archive-index.json').read_text());entry=index['issuers'][code]
  path=(self.base/entry['file']).resolve();path.relative_to(self.base)
  if code not in self.cache:
   raw=path.read_bytes()
   if hashlib.sha256(raw).hexdigest()!=entry['sha256']:raise ValueError('BROWSER_EVIDENCE_ARCHIVE_SHA')
   z=zipfile.ZipFile(io.BytesIO(raw))
   if len(z.namelist())!=len(set(z.namelist())):raise ValueError('BROWSER_EVIDENCE_DUPLICATE_PATH')
   self.cache[code]=z
  return self.cache[code].read(name)
def pack(proof):
 proof=Path(proof);q=json.loads(proof.read_text());index={'schema':'financials.real_browser_archive.v1','issuers':{}}
 for code in q['issuers']:
  files={f[k] for c in q['cases'] if c['issuer']==code for f in c['figures'] for k in ('screenshot_file','export_file')}
  path=proof.parent/(code+'-actual-browser-evidence.zip')
  with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
   for name in sorted(files):z.write(proof.parent/name,name)
  index['issuers'][code]={'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size,'original_files':len(files)}
 (proof.parent/'archive-index.json').write_text(json.dumps(index,indent=2)+'\n')
 return index

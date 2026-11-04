"""Resolve preserved November calibration materials by exact content hash."""
from pathlib import Path
import hashlib,json

WORK=Path(__file__).resolve().parents[6]
ROOT=WORK/'graduation-experiment-results/chapter2_retrieval'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def preserved(relative,expected):
    live=(WORK/relative).resolve()
    if not live.is_relative_to(WORK):raise ValueError('Evidence path outside workspace')
    if live.is_file() and sha(live)==expected:return live
    for manifest in (ROOT/'release/frozen').glob('*/calibration_materials/manifest.json'):
        value=json.loads(manifest.read_text('utf-8'))
        if value['files'].get(relative)!=expected:continue
        path=(manifest.parent/value['stored_files'][relative]).resolve()
        if not path.is_relative_to(manifest.parent.resolve()) or sha(path)!=expected:raise ValueError('Archived evidence hash mismatch')
        return path
    raise ValueError('No matching preserved evidence: '+relative)

def material(relative,protocol):
    manifest=ROOT/'release/frozen'/protocol/'calibration_materials/manifest.json'
    value=json.loads(manifest.read_text('utf-8'))
    path=manifest.parent/value['stored_files'][relative]
    if sha(path)!=value['files'][relative]:raise ValueError('Preserved material drift')
    return path

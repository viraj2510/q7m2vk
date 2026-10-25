"""Explicit refresh of the archived cohort; never runs during web requests."""
import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

root=Path(__file__).parent
base='https://data.elexon.co.uk/bmrs/api/v1/datasets/'
urls={
 'windfor.json':base+'WINDFOR/stream?publishDateTimeFrom=2025-12-31T00:00:00Z&publishDateTimeTo=2026-02-01T00:00:00Z',
 'fuelhh.json':base+'FUELHH/stream?settlementDateFrom=2026-01-02&settlementDateTo=2026-02-01&fuelType=WIND'
}
if __name__=='__main__':
    manifest={'retrievedAt':datetime.now(timezone.utc).isoformat(),'files':{}}
    for name,url in urls.items():
        with urllib.request.urlopen(url,timeout=120) as response: content=response.read()
        rows=json.loads(content)
        if not isinstance(rows,list) or not rows: raise ValueError('Expected nonempty stream')
        (root/name).write_bytes(content)
        manifest['files'][name]={'url':url,'rows':len(rows),'sha256':hashlib.sha256(content).hexdigest()}
    (root/'manifest.json').write_text(json.dumps(manifest,indent=2))

"""Reconstruct reviewed original commits exactly; never modify main."""
from pathlib import Path
from hashlib import sha256
import json
import lzma
import subprocess

folder = Path(__file__).resolve().parent
packed = b''.join((folder / f'part{i}.bin').read_bytes() for i in range(4))
assert sha256(packed).hexdigest() == '58289d0fbd81ce40bfb77bf0054a02b708b9ec604524b6fd3ede489cb61b7413'
rows = json.loads(lzma.decompress(packed))
expected = ['49f8747e00e9c57c98a5c664501a8f2cdd01227b', '9e160e626925d41a45178ba4ffb4862a8c9ec0ea', '628f203d4a3822ffbfc00ca3a2f3303b3c924fbd', 'd45677080b58459ca6b008431ae1f168ac2045d9', 'cd6792dc77f2e08038c88ffb6886c9a78ab734d6', 'b60aa7b209aab68cd28651d2c43a674271f67db8']
assert [r['sha'] for r in rows] == expected

def git(*args, data=None):
    return subprocess.check_output(['git', *args], input=data)

for row in rows:
    raw = row['commit'].encode('utf-8')
    header = row['commit'].split('\n\n', 1)[0].splitlines()
    parent = next(s[7:] for s in header if s.startswith('parent '))
    tree = next(s[5:] for s in header if s.startswith('tree '))
    assert git('hash-object', '-t', 'commit', '--stdin', data=raw).decode().strip() == row['sha']
    git('checkout', '--detach', parent)
    patch = row['patch'].encode('utf-8')
    if patch:
        git('apply', '--check', '--index', '-', data=patch)
        git('apply', '--index', '-', data=patch)
    changed = git('diff', '--cached', '--name-only').decode().splitlines()
    assert all(p.startswith(('src/i3/', 'tests/i3/', 'docs/decisions/ADR-0015-')) for p in changed), changed
    assert git('write-tree').decode().strip() == tree, row['sha']
    assert git('hash-object', '-w', '-t', 'commit', '--stdin', data=raw).decode().strip() == row['sha']
    git('checkout', '--detach', row['sha'])
    print('EXACT_ORIGINAL_COMMIT', row['sha'], 'TREE', tree)
assert not git('status', '--porcelain').strip()

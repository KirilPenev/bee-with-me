"""Stub `python -m backend.db.migrate` for the start-script tests (runs from the temp project copy).

`status` exits with the next code of $BWM_STUB_MIGRATE_EXITS (comma-separated; the last one repeats);
`up` exits with $BWM_STUB_MIGRATE_UP_EXIT (default 0). Every call logs "migrate <args>" to $BWM_STUB_LOG.
BWM_STUB_MIGRATE_WARN=1 also writes a warning to stderr.
"""

import os
import sys
from pathlib import Path

log = Path(os.environ['BWM_STUB_LOG'])
if sys.argv[1:] == ['up']:
    with log.open('a', encoding='utf-8') as f:
        f.write('migrate up\n')
    sys.exit(int(os.environ.get('BWM_STUB_MIGRATE_UP_EXIT', '0')))
codes = [int(c) for c in os.environ.get('BWM_STUB_MIGRATE_EXITS', '0').split(',')]
counter = log.with_name(log.name + '.migrate-count')
n = int(counter.read_text()) if counter.exists() else 0
counter.write_text(str(n + 1))
with log.open('a', encoding='utf-8') as f:
    f.write('migrate ' + ' '.join(sys.argv[1:]) + '\n')
if os.environ.get('BWM_STUB_MIGRATE_WARN') == '1':
    print('WARNING: stub migrate: something on stderr', file=sys.stderr)
print(f'stub migrate: exit {codes[min(n, len(codes) - 1)]}')
sys.exit(codes[min(n, len(codes) - 1)])

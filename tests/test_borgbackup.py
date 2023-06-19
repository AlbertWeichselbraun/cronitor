import gzip
from datetime import timedelta, datetime

from cronitor.borgbackup import BorgBackup
from pathlib import Path

EXAMPLE_OUTPUT = gzip.open(Path(__file__).parent / 'data' / 'borgbackup.json.gz', 'rt').read()

def test_parse_borgbackup_output():
    backups = BorgBackup.parse_borgbackup_ouptut(EXAMPLE_OUTPUT, max_age=timedelta(days=7))
    print(backups)
    assert backups == {
        'immanuel.fhgr.ch': [datetime(2023, 6, 17, 15, 30, 14), datetime(2023, 6, 18, 15, 30, 15), datetime(2023, 6, 19, 15, 30, 12)],
        'immanuel.albert.priv.at': [],
        'ubuntu.albert.priv.at': [],
        'epiphany.albert.priv.at': [],
        'epiphany': [],
    }
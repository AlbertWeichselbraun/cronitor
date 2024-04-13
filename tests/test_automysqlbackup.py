import gzip
from cronvisio.monitor.automysqlbackup import AutoMysqlBackup
from datetime import timedelta, datetime

from cronvisio.monitor.borgbackup import BorgBackupMonitor
from pathlib import Path

AUTOMYSQLBACKUP_TEST_DIR = Path(__file__).parent / "data" / "automysqlbackup"


def test_parse_borgbackup_output():
    # working backup does not produce a notification
    backups = AutoMysqlBackup(
        archive_path=AUTOMYSQLBACKUP_TEST_DIR,
        max_age=1,
        date=datetime(year=2023, month=9, day=9),
    )
    assert backups.notify() == ""

    backups = AutoMysqlBackup(
        archive_path=AUTOMYSQLBACKUP_TEST_DIR,
        max_age=1,
        date=datetime(year=2023, month=9, day=10),
    )
    assert backups.notify() == ""

    # this backup is one day too old
    backups = AutoMysqlBackup(
        archive_path=AUTOMYSQLBACKUP_TEST_DIR,
        max_age=1,
        date=datetime(year=2023, month=9, day=11),
    )
    print(backups.notify())
    assert "2023-09-09" in backups.notify()

#!/usr/bin/env python3

import re
from datetime import datetime, timedelta
from pathlib import Path

from cronvisio.monitor import Monitor

RE_DATE = re.compile(r"[\._](\d{4}-\d{2}-\d{2})[\._]")


class AutoMysqlBackup(Monitor):

    def __init__(
        self, archive_path: Path, max_age: int, date: datetime = datetime.now()
    ):
        """
        Args:
            max_age: maximum backup age to consider in days.
            ignore_hosts: hosts to ignore (i.e., we won't trigger an alert if no backup has been conducted within
                max_age for the hosts).
        """
        self.archive_path = Path(archive_path)
        self.date_threshold = date - timedelta(days=max_age)

    def notify(self, force=False):
        msg = []

        # determine the date of the most recent backup
        most_current_date = datetime.strptime("1900-01-01", "%Y-%m-%d")
        for path in self.archive_path.rglob("*.sql.gz"):
            date = datetime.strptime(
                RE_DATE.search(str(path.name)).group(1), "%Y-%m-%d"
            )
            if date > most_current_date:
                most_current_date = date

        if most_current_date < self.date_threshold or force:
            msg.append(
                "\n# WARNING: No recent automysql database backup found.\n"
                f"           Date of last backup: {most_current_date.date().isoformat()}"
            )
        return "\n".join(msg)

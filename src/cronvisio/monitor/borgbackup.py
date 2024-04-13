#!/usr/bin/env python3

import subprocess

from datetime import datetime, timedelta
from json import loads
from pathlib import Path

from cronvisio.monitor import Monitor


class BorgBackupMonitor(Monitor):

    def __init__(
        self,
        archive_path: Path,
        max_age: int,
        min_backup_count: int = 0,
        ignore_archives: list[str] = tuple(),
        ignore_hosts: list[str] = tuple(),
    ):
        """
        Args:
            max_age: maximum backup age to consider in days.
            ignore_hosts: hosts to ignore (i.e., we won't trigger an alert if no backup has been conducted within
                max_age for the hosts).
        """
        self.archive_path = Path(archive_path)
        self.max_age = timedelta(days=max_age)
        self.min_backup_count = min_backup_count
        self.ignore_archives = ignore_archives
        self.ignore_hosts = ignore_hosts

    def notify(self, force=False):
        msg = []
        for path in self.archive_path.glob("*"):
            if not path.is_dir() or path.name in self.ignore_archives:
                continue
            backups = self.parse_borgbackup_output(
                subprocess.check_output(["borg", "list", "--json", str(path)]).decode(
                    "utf-8"
                )
            )
            notification_required = any(
                (
                    host
                    for host, last_backups in backups.items()
                    if self.min_backup_count
                    and len(last_backups) < self.min_backup_count
                )
            )
            if notification_required or force:
                msg.append(f"\n# Backups in archive {path}:")
                msg += [
                    f'- {host}: {", ".join(b.strftime("%Y-%m-%d") for b in last_backups)}'
                    for host, last_backups in backups.items()
                ]
        return "\n".join(msg)

    def parse_borgbackup_output(
        self, out: str, current_date: datetime = datetime.now()
    ):
        """
        Returns:
          A map of hostnames and the corresponding backups.
        """
        archives = {}
        cutoff_date = current_date - self.max_age
        for archive in loads(out)["archives"]:
            backup_host = archive["name"].rsplit(".", 1)[0]
            if (
                backup_host not in archives
                and backup_host
                and backup_host not in self.ignore_hosts
            ):
                archives[backup_host] = []
            date = datetime.strptime(archive["start"], "%Y-%m-%dT%H:%M:%S.%f")
            if not self.max_age or date >= cutoff_date:
                archives[backup_host].append(date)
        return archives

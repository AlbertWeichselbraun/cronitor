#!/usr/bin/env python3

import logging
from collections import defaultdict
from datetime import datetime, timedelta
from json import loads
import subprocess

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)


class BorgBackup:
    measurement_name = 'queue'
    sensor_tags = {'sensor': 'postfix_queue'}

    @staticmethod
    def parse_borgbackup_ouptut(out: str, current_date: datetime = datetime.now(), max_age: timedelta = timedelta()):
        """
        Returns:
          A map of hostnames and the corresponding backups.
        """
        archives = {}
        cutoff_date = current_date - max_age
        for archive in loads(out)['archives']:
            backup_host = archive['name'].rsplit('.', 1)[0]
            if backup_host not in archives and backup_host:
                archives[backup_host] = []
            date = datetime.strptime(archive['start'], "%Y-%m-%dT%H:%M:%S.%f")
            if not max_age or date >= cutoff_date:
                archives[backup_host].append(date)
        return archives

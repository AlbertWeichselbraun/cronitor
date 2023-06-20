#!/usr/bin/env python
"""
Cronitor
"""
import sys
from json import load

from cronitor import Cronitor
from cronitor.monitor.postfix import PostfixMonitor
from cronitor.monitor.borgbackup import BorgBackupMonitor
from cronitor.monitor.tlsreport import TLSReportMonitor
from cronitor.notifier.matrix import MatrixNotifier

if len(sys.argv) < 2:
    print(f'{sys.argv[0]} [hourly|daily|weekly]')
    sys.exit(-1)

config = load(open('cronitor.json'))
notifiers = [MatrixNotifier(**config['matrix'])]
match sys.argv[1]:
    case 'hourly':
        monitors = [PostfixMonitor()]
        Cronitor.cronitor(monitors, notifiers, force=True)
    case 'daily':
        monitors = [TLSReportMonitor(**config['tlsreport_monitor'])]
        Cronitor.cronitor(monitors, notifiers, force=True)
    case 'weekly':
        monitors = [BorgBackupMonitor(**config['borgbackup_monitor'])]
        Cronitor.cronitor(monitors, notifiers=notifiers, force=True)
    case _:
        print(f'Unsupported parameter {sys.argv[1]}.')
        sys.exit(-1)

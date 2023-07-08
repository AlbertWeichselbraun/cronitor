#!/usr/bin/env python
"""
Cronitor
"""
import sys
from json import load

from cronitor import Cronitor
from cronitor.monitor.amazon_kindle_quotes import AmazonKindleQuotes
from cronitor.monitor.postfix import PostfixMonitor
from cronitor.monitor.borgbackup import BorgBackupMonitor
from cronitor.monitor.tlsreport import TLSReportMonitor
from cronitor.notifier.matrix import MatrixNotifier

if len(sys.argv) < 2:
    print(f'{sys.argv[0]} [hourly|daily|weekly]')
    sys.exit(-1)

config = load(open('cronitor.json'))
update_notifiers = [MatrixNotifier(**config['matrix']['updates'])]
delight_notifier = [MatrixNotifier(**config['matrix']['delight'])]
match sys.argv[1]:
    case 'hourly':
        # postfix
        monitors = [PostfixMonitor()]
        Cronitor.cronitor(monitors, update_notifiers)
        # kindle
        monitors = [AmazonKindleQuotes(**config['amazon_kindle_quotes'])]
        Cronitor.cronitor(monitors, delight_notifier)
    case 'daily':
        monitors = [TLSReportMonitor(**config['tlsreport_monitor'])]
        Cronitor.cronitor(monitors, update_notifiers)
    case 'weekly':
        monitors = [PostfixMonitor(), TLSReportMonitor(**config['tlsreport_monitor']),
                    BorgBackupMonitor(**config['borgbackup_monitor'])]
        Cronitor.cronitor(monitors, notifiers=update_notifiers, force=True)
    case _:
        print(f'Unsupported parameter {sys.argv[1]}.')
        sys.exit(-1)

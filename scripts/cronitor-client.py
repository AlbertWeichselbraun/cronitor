#!/usr/bin/env python
"""
Cronitor
"""
import sys
from json import load

from cronitor import Cronitor
from cronitor.monitor.postfix import PostfixMonitor
from cronitor.monitor.borgbackup import BorgBackupMonitor
from cronitor.notifier.stdout import StdoutNotifier

if len(sys.argv) < 2:
    print(f'{sys.argv[0]} [hourly|weekly]')

config = load(open('cronitor.json'))
match sys.argv[1]:
    case 'hourly':
        monitors = [PostfixMonitor()]
        notifiers = [StdoutNotifier()]
        Cronitor.cronitor(monitors, notifiers, force=True)
    case 'weekly':
        monitors = [BorgBackupMonitor(*config['borgbackup_monitor'])]
        notifiers = [StdoutNotifier()]
        Cronitor.cronitor(monitors, notifiers=notifiers, force=True)
    case _:
        print(f'Unsupported parameter {sys.argv[1]}.')
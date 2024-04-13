#!/usr/bin/env python
"""
Cronitor
"""
import sys
from json import load

from cronvisio import Cronitor
from cronvisio.monitor.amazon_kindle_quotes import AmazonKindleQuotes
from cronvisio.monitor.automysqlbackup import AutoMysqlBackup
from cronvisio.monitor.postfix import PostfixMonitor
from cronvisio.monitor.borgbackup import BorgBackupMonitor
from cronvisio.monitor.tlsreport import TLSReportMonitor
from cronvisio.notifier.matrix import MatrixNotifier


def cli():
    if len(sys.argv) < 2:
        print(f"{sys.argv[0]} [hourly|daily|weekly] [nonotify]")
        sys.exit(-1)

    config = load(open("cronvisio.json"))

    # optional: disable notifications for debuging
    if len(sys.argv) > 2 and sys.argv[2] == "nonotify":
        from cronvisio.notifier.stdout import StdoutNotifier

        update_notifiers = [StdoutNotifier()]
        delight_notifier = [StdoutNotifier()]
    else:
        update_notifiers = [MatrixNotifier(**config["matrix"]["updates"])]
        delight_notifier = [MatrixNotifier(**config["matrix"]["delight"])]

    match sys.argv[1]:
        case "hourly":
            # postfix
            # monitors = [PostfixMonitor()]
            # Cronitor.cronvisio(monitors, update_notifiers)
            # kindle
            monitors = [AmazonKindleQuotes(**config["amazon_kindle_quotes"])]
            Cronitor.cronitor(monitors, delight_notifier)
        case "daily":
            monitors = [
                TLSReportMonitor(**config["tlsreport_monitor"]),
                AutoMysqlBackup(**config["automysqlbackup_monitor"]),
            ]
            Cronitor.cronitor(monitors, update_notifiers)
        case "weekly":
            monitors = [
                PostfixMonitor(),
                TLSReportMonitor(**config["tlsreport_monitor"]),
                BorgBackupMonitor(**config["borgbackup_monitor"]),
            ]
            Cronitor.cronitor(monitors, notifiers=update_notifiers, force=True)
        case _:
            print(f"Unsupported parameter {sys.argv[1]}.")
            sys.exit(-1)


if __name__ == "__main__":
    cli()

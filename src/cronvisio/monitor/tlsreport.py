#!/usr/bin/env python3

import email
from collections import defaultdict
from datetime import date, timedelta
from gzip import decompress
from imaplib import IMAP4, IMAP4_SSL
from json import loads

from cronvisio.monitor import Monitor


class TLSReportMonitor(Monitor):
    def __init__(
        self,
        imap_server: str,
        imap_user: str,
        imap_pass: str,
        imap_filter: str,
        max_age: int,
    ):
        self.imap_server = imap_server
        self.imap_user = imap_user
        self.imap_pass = imap_pass
        self.imap_filter = imap_filter
        self.since = date.today() - timedelta(days=max_age)

    def compute_stats(self):
        """
        Returns:
            The number of failures and a dictionary with per reporter and
            domain statistics.
        """
        stats = defaultdict(dict)
        failures = 0
        with IMAP4_SSL(self.imap_server) as imap:
            imap.login(self.imap_user, self.imap_pass)
            imap.select("INBOX")
            _, messages = imap.search(
                None,
                "({} SINCE {})".format(self.imap_filter, self.since.strftime("%d-%b-%Y")),
            )
            for msg in messages[0].split(b" "):
                _, data = imap.fetch(msg, "(RFC822)")

                for response in data:
                    if isinstance(response, tuple):
                        msg = email.message_from_bytes(response[1])

                        if not msg.is_multipart():
                            print("Message is not multipart!")
                            continue

                        for part in msg.walk():
                            content_disposition = str(part.get("Content-Disposition"))
                            if content_disposition.startswith("attachment"):
                                content = part.get_payload(decode=True)
                                content = decompress(content)
                                j = loads(content)

                                reporter = j["contact-info"]
                                for policy in j["policies"]:
                                    domain = policy["policy"]["policy-domain"]
                                    if domain not in stats[reporter]:
                                        stats[reporter][domain] = {}
                                    stats[reporter][domain]["successful"] = (
                                        stats[reporter][domain].get("successful", 0)
                                        + policy["summary"]["total-successful-session-count"]
                                    )
                                    stats[reporter][domain]["failure"] = (
                                        stats[reporter][domain].get("failure", 0)
                                        + policy["summary"]["total-failure-session-count"]
                                    )
                                    failures += policy["summary"]["total-failure-session-count"]

        return failures, stats

    def format_statisics(self, stats, failures):
        """
        Format the TLS reporting statistics.
        """
        r = []
        if failures > 0:
            r.append(
                f"# {failures} TLS Errors reported between {self.since.isoformat()} and {date.today().isoformat()}!\n"
            )
        else:
            r.append(f"# Mail statistics: {self.since.isoformat()} to {date.today().isoformat()}:\n")

        for no, reporter in enumerate(stats, 1):
            r.append(f"{no}. {reporter}")
            r.append(
                "   - {}: successful: {}, failure: {}".format(
                    domain,
                    stats[reporter][domain]["successful"],
                    stats[reporter][domain]["failure"],
                )
                for domain in stats[reporter]
            )
        return "\n".join(r)

    def notify(self, force=True):
        try:
            failures, stats = self.compute_stats()
        except IMAP4.error as e:
            return "WARNING: failed to access the impact account - " + str(e)

        if failures > 0 or force:
            return self.format_statisics(stats, failures)
        return ""

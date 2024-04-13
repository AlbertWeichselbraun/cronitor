#!/usr/bin/env python3

import email
from datetime import date, timedelta
from hashlib import md5
from imaplib import IMAP4_SSL
from quopri import decodestring

from cronvisio.monitor import Monitor

QUOTE_CACHE_FILE = ".cronvisio-known-amazon-kindle-quotes"


class AmazonKindleQuotes(Monitor):

    def __init__(self, imap_server: str, imap_user: str, imap_pass: str, max_age: int):
        self.imap_server = imap_server
        self.imap_user = imap_user
        self.imap_pass = imap_pass
        self.since = date.today() - timedelta(days=max_age)
        try:
            self.known_quote_hashes = open(QUOTE_CACHE_FILE).read().split()
        except FileNotFoundError:
            self.known_quote_hashes = []

    def is_known_quote(self, quote):
        """
        Checks whether the given quote is known.
        """
        quote_hash = md5(quote.encode("utf8"), usedforsecurity=False).hexdigest()
        if quote_hash in self.known_quote_hashes:
            return True

        open(QUOTE_CACHE_FILE, "a").write(quote_hash + "\n")
        return False

    @staticmethod
    def extract_quote(text):
        """
        Extract the quote from the given text.

        Note:
            The Kindle puts the quote text under quotation marks.
        """
        result = []
        in_quote = False
        for line in text.split("\n"):
            if line.startswith('"'):
                in_quote = True
            elif in_quote and not line.strip():
                in_quote = False

            if in_quote:
                result.append(line.strip())

        return " ".join(result)

    def get_quotes(self):
        """
        Returns:
            The number of failures and a dictionary with per reporter and
            domain statistics.
        """
        result = []
        with IMAP4_SSL(self.imap_server) as imap:
            imap.login(self.imap_user, self.imap_pass)
            imap.select("INBOX")
            _, messages = imap.search(
                None, "(SINCE {})".format(self.since.strftime("%d-%b-%Y"))
            )
            for msg in messages[0].split(b" "):
                _, data = imap.fetch(msg, "(RFC822)")

                for response in data:
                    if isinstance(response, tuple):
                        msg = email.message_from_bytes(response[1])
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                if (
                                    part.get("Content-Transfer-Encoding", "utf8")
                                    == "quoted-printable"
                                ):
                                    mail_content = self.extract_quote(
                                        decodestring(part.get_payload()).decode("utf8")
                                    )
                                else:
                                    mail_content = self.extract_quote(
                                        part.get_payload()
                                    )
                        quote = self.extract_quote(mail_content)
                        if not self.is_known_quote(quote):
                            result.append(quote)
        return result

    def notify(self, force=True):
        return self.get_quotes()


if __name__ == "__main__":
    from json import load

    config = load(open("cronvisio.json"))
    akq = AmazonKindleQuotes(**config["amazon_kindle_quotes"])
    print(akq.get_quotes())

#!/usr/bin/env python3
from collections import defaultdict
from imaplib import IMAP4_SSL, IMAP4
from datetime import date, timedelta
from cronitor.monitor import Monitor
from hashlib import md5
import email

QUOTE_CACHE_FILE = '.cronitor-known-amazon-kindle-quotes'

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
        quote_hash = md5(quote.encode('utf8'), usedforsecurity=False).hexdigest()
        if quote_hash in self.known_quote_hashes:
            return True

        open(QUOTE_CACHE_FILE, 'a').write(quote_hash + '\n')
        return False

    @staticmethod
    def get_quote(text):
        """
        Extract the quote from the given text.

        Note:
            The Kindle puts the quote text under quotation marks.
        """
        result = []
        in_quote = False
        for line in text.split('\n'):
            if line.startswith('"'):
                in_quote = True
            elif in_quote and not line.strip():
                in_quote = False

            if in_quote:
                result.append(line.strip())

        return ' '.join(result)

    def get_quotes(self):
        """
        Returns:
            The number of failures and a dictionary with per reporter and
            domain statistics.
        """
        result = []
        with IMAP4_SSL(self.imap_server) as imap:
            imap.login(self.imap_user, self.imap_pass)
            imap.select('INBOX')
            _, messages = imap.search(None, '(SINCE {})'.format(self.since.strftime("%d-%b-%Y")))
            for msg in messages[0].split(b' '):
                _, data = imap.fetch(msg, '(RFC822)')

                for response in data:
                    if isinstance(response, tuple):
                        msg = email.message_from_bytes(response[1])
                        quote = self.get_quote(msg.get_payload())
                        if not self.is_known_quote(quote):
                            result.append(quote)
        return result

    def notify(self, force=True):
        try:
            failures, stats = self.get_quotes()
        except IMAP4.error as e:
            return 'WARNING: failed to access the impact account - ' + str(e)

        if failures > 0 or force:
            return self.format_statisics(stats, failures)
        return ''


if __name__ == '__main__':
    from json import load
    config = load(open('cronitor.json'))
    akq = AmazonKindleQuotes(**config['amazon_kindle_quotes'])
    quotes = akq.get_quotes()
    print(quotes)

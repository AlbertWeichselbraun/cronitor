import gzip
from pathlib import Path

from cronvisio.monitor.amazon_kindle_quotes import AmazonKindleQuotes

KINDLE_EXAMPLES = Path(__file__).parent / "data" / "kindle"


def test_parse_borgbackup_output():
    for example in KINDLE_EXAMPLES.glob("*.txt.gz"):
        text = gzip.open(example, mode="rt").read()

        extracted_text = AmazonKindleQuotes.extract_quote(text)
        print(extracted_text)

        assert "//amzn.eu" not in extracted_text
        assert "//amzn.to" not in extracted_text

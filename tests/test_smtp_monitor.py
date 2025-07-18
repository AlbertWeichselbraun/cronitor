from unittest.mock import patch

from cronvisio.monitor.smtp import SmtpMonitor


def test_working_smtp_server():
    with patch("smtplib.SMTP") as mock_smtp:
        smtp_connection = mock_smtp.return_value
        smtp_connection.noop.return_value = (250, b"OK")
        smtp_connection.quit.return_value = (221, b"Goodbye")

        smtp_monitor = SmtpMonitor(host="localhost")
        assert smtp_monitor.check_smtp_connection()


def test_unavailable_smtp_server():
    smtp_monitor = SmtpMonitor(host="localhost", timeout=1)
    assert not smtp_monitor.check_smtp_connection()

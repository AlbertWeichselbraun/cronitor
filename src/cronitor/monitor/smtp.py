from cronitor.monitor import Monitor
from smtplib import SMTP

TIMEOUT = 5  # default timeout: 5 seconds


class SmtpMonitor(Monitor):
    def __init__(self, host: str, outgoing_ip: str, timeout: int = TIMEOUT):
        self.host = host
        self.outgoing_ip = outgoing_ip
        self.timeout = timeout

    def notify(self, force=True):
        if self.check_smtp_connection():
            return ""
        return f"# SMTP monitoring:\n- Connection to {self.host} via {self.outgoing_ip} failed after {self.timeout} seconds."

    def check_smtp_connection(self):
        """
        Checks whether the SMTP connection to the host is successful.

        Returns:
            bool: True, if successful, False otherwise.
        """
        try:
            with SMTP(
                self.host, source_address=(self.outgoing_ip, 0), timeout=self.timeout
            ) as s:
                s.noop()
                s.quit()
                return True
        except TimeoutError:
            return False

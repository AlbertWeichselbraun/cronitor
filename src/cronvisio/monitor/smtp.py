import smtplib
from typing import Tuple

from cronvisio.monitor import Monitor

TIMEOUT = 5  # default timeout: 5 seconds


class SmtpMonitor(Monitor):
    def __init__(
        self,
        host: str,
        outgoing_ip: Tuple[str, int] = ("0.0.0.0", 0),
        timeout: int = TIMEOUT,
    ):
        """
        Args:
            host: the name of the host to connect to.
            outgoing_ip: ip to use for outgoing traffic or 0.0.0.0 for default.
            timeout: timeout in seconds.
        """
        self.host = host
        self.outgoing_ip = outgoing_ip
        self.timeout = timeout

    def notify(self, force: bool = True) -> str:
        if self.check_smtp_connection():
            return ""
        return (
            f"# SMTP monitoring:\n- Connection to {self.host} via {self.outgoing_ip} failed "
            f"after {self.timeout} seconds."
        )

    def check_smtp_connection(self) -> bool:
        """
        Checks whether the SMTP connection to the host is successful.

        Returns:
            bool: True, if successful, False otherwise.
        """
        try:
            s = smtplib.SMTP(self.host, source_address=None, timeout=self.timeout)
            s.noop()
            s.quit()
            return True
        except (TimeoutError, ConnectionError) as _:
            return False

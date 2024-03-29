from abc import abstractmethod


class Monitor:
    @abstractmethod
    def notify(self, force: bool = True) -> str:
        """
        Args:
            force: return the notification message even if no thresholds have been violated.

        Returns:
            str: The notification message to send.
        """

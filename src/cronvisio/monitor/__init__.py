from abc import abstractmethod


class Monitor:

    @abstractmethod
    def notify(self, force=True) -> str:
        """
        Args:
            force: return the notification message even if no thresholds have been violated.

        Returns:
            The notification message to send.
        """

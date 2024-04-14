from abc import abstractmethod


class Monitor:
    @abstractmethod
    def notify(self, force: bool = True) -> str:
        """
        Args:
            force: return the notification message even if no thresholds have been violated.

        Returns:
<<<<<<< HEAD:src/cronvisio/monitor/__init__.py
            The notification message to send.
=======
            str: The notification message to send.
>>>>>>> feature/wireguard:src/cronitor/monitor/__init__.py
        """

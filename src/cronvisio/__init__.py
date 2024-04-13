from cronvisio.monitor import Monitor
from cronvisio.notifier import Notifier


class Cronitor:

    @staticmethod
    def cronitor(
        monitors: list[Monitor], notifiers: list[Notifier], force: bool = False
    ):
        """
        Args:
            monitors: a list of monitors to monitor
            notifiers: a list of notifiers used for sending notifications.
            force: whether to force notifications
        """
        messages = list(filter(None, [m.notify(force) for m in monitors]))
        if not messages:
            return

        for n in notifiers:
            n.send_notifications(messages)

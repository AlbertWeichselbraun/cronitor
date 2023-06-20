from cronitor.monitor import Monitor
from cronitor.notifier import Notifier


class Cronitor:

    @staticmethod
    def cronitor(monitors: list[Monitor], notifiers: list[Notifier], force: bool = False):
        """
        Args:
            monitors: a list of monitors to monitor
            notifiers: a list of notifiers used for sending notifications.
            force: whether to force notifications
        """
        msg = '\n\n'.join([m.notify(force) for m in monitors])
        if not msg:
            return

        for n in notifiers:
            n.send_notification(msg)

from cronitor import Notifier


class StdoutNotifier(Notifier):

    def send_notification(self, msg):
        print(msg)
from cronvisio import Notifier


class StdoutNotifier(Notifier):

    def send_notifications(self, messages):
        for msg in messages:
            print("\n".join(msg))

from abc import abstractmethod


class Notifier:

    @abstractmethod
    def send_notifications(self, msg):
        pass

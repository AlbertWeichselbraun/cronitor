from abc import abstractmethod


class Notifier:

    @abstractmethod
    def send_notification(self, msg):
        pass

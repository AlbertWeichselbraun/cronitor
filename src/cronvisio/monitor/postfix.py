#!/usr/bin/env python3

import subprocess

from cronvisio.monitor import Monitor


class PostfixMonitor(Monitor):
    def notify(self, force=True):
        if queue_size := self.get_queue_size():
            return f"# Mail monitoring:\n- {queue_size} mails are currently queued."
        if force:
            return "# Mail monitoring:\n- Mail queue is empty."
        return ""

    @staticmethod
    def get_queue_size():
        """
        Returns:
          A key, value mapping of sensor data.
        """
        output = subprocess.check_output(["postqueue", "-p"]).decode("utf-8")
        # one line per item  header
        return len(output.splitlines()) - 1


if __name__ == "__main__":
    print(PostfixMonitor.get_queue_size())

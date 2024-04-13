#!/usr/bin/env python3

import subprocess
from cronvisio.monitor import Monitor


class PostfixMonitor(Monitor):

    def notify(self, force=True):
        if queue_size := self.get_queue_size():
            return f"# Mail monitoring:\n- {queue_size} mails are currently queued."
        elif force:
            return "# Mail monitoring:\n- Mail queue is empty."
        else:
            return ""

    @staticmethod
    def get_queue_size():
        """
        Returns:
          A key, value mapping of sensor data.
        """
        output = subprocess.check_output(["postqueue", "-p"]).decode("utf-8")
        # one line per item  header
        queue_size = len(output.splitlines()) - 1
        return queue_size


if __name__ == "__main__":
    print(PostfixMonitor.get_queue_size())

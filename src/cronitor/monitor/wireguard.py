#!/usr/bin/env python3
"""
Check and repair wireguard interfaces that have been frozen due to a change of the endpoint's IP address.
"""
import configparser
import subprocess
from collections import namedtuple
from glob import glob
from time import time
from typing import Optional

from cronitor import Monitor

WL_HANDSHAKE = ["wg", "show", "all", "latest-handshakes"]

DEFAULT_CONFIG_DIR = '/etc/wireguard'
DEFAULT_TIMEOUT = 150

EndPoint = namedtuple("EndPoint", "host port")


class WireguardMonitor(Monitor):

    def __init__(self, wireguard_config_dir=DEFAULT_CONFIG_DIR, timeout=DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.interfaces = {name.split('.conf')[0]: self.read_host_from_wl_config(name)
                           for name in glob(f'{wireguard_config_dir}/*.conf')}

    def notify(self, force=True):
        """
        Check all configured wiregard interfaces and notify the user of frozen ones.
        """



        if queue_size := self.get_queue_size():
            return f'# Mail monitoring:\n- {queue_size} mails are currently queued.'
        elif force:
            return '# Mail monitoring:\n- Mail queue is empty.'
        else:
            return ''

    @staticmethod
    def read_host_from_wl_config(fname: str) -> Optional[EndPoint]:
        """
        Determine the endpoints for all configured client wireguard interfaces.
        (i.e., only the interfaces that connect to an endpoint).

        Args:
             fname: path to wireguard configuration file.

        Returns:
            An Endpoint tuple which consists of the host and port of the endpoint.
        """
        config = configparser.ConfigParser()
        config.read_file(fname)
        try:
            return EndPoint(*config.get('Peer', 'Endpoint').split(':'))
        except configparser.NoOptionError:
            return None

    @staticmethod
    def read_wg_status(namespace: str = None):
        """
        Determine the status of all wireguard connections on the given host.

        Example output:
        wg-de	KEY=	1708807507

        Returns:
            A list of 'interface' and 'time since last handshake' tuples.
        """
        cmd = WL_HANDSHAKE if not namespace else ['ip', 'netns', 'exec', namespace] + WL_HANDSHAKE
        return [(iface, time() - int(timestamp))
                for line in subprocess.run(cmd, check=True, capture_output=True, text=True).stdout.split('\n')
                for iface, _, timestamp in line.split()]


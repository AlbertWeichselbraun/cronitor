#!/usr/bin/env python3
import configparser
import subprocess
from glob import glob
from time import time

from cronitor import Monitor

WL_HANDSHAKE = ["wg", "show", "all", "latest-handshakes"]

DEFAULT_CONFIG_DIR = '/etc/wireguard'
DEFAULT_TIMEOUT = 150


class WireguardMonitor(Monitor):

    def __init__(self, wireguard_config_dir=DEFAULT_CONFIG_DIR, timeout=DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.interfaces = {name.split('.conf')[0]: self.read_host_from_wl_config(name)
                           for name in glob(f'{wireguard_config_dir}/*.conf')}

    @staticmethod
    def read_host_from_wl_config(fname: str):
        config = configparser.ConfigParser()
        config.read_file(fname)
        try:
            return config.get('Peer', 'Endpoint').split(':')[0]
        except configparser.NoOptionError:
            return None

    @staticmethod
    def read_wg_status(namespace: str = None):
        """

        Example output:
        wg-de	KEY=	1708807507

        Returns:
            A list of 'interface' and 'time since last handshake' tuples.
        """
        cmd = WL_HANDSHAKE if not namespace else ['ip', 'netns', 'exec', namespace] + WL_HANDSHAKE

        return [(iface, time() - int(timestamp))
                for line in subprocess.run(cmd, check=True, capture_output=True, text=True).stdout.split('\n')
                for iface, _, timestamp in line.split()]

    def notify(self, force=True):
        pass

import gzip
from datetime import timedelta, datetime
from os.path import dirname

from cronitor.monitor.borgbackup import BorgBackupMonitor
from pathlib import Path

from cronitor.monitor.wireguard import WireguardMonitor, EndPoint

WIREGUARD_CONFIG_DIR = dirname(__file__) + "/data/wireguard"


def test_wireguard_cronitor():
    wg = WireguardMonitor(wireguard_config_dir=WIREGUARD_CONFIG_DIR)
    print(wg.interfaces)
    assert wg.interfaces == {
        "client1": EndPoint(host="localhost", port="8888"),
        "server": None,
        "client2": EndPoint(host="localhost", port="51820"),
    }

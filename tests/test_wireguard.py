from os.path import dirname
from pathlib import Path
from unittest.mock import patch, MagicMock

from cronitor.monitor.wireguard import WireguardMonitor, EndPoint, WireGuardInterface

WIREGUARD_CONFIG_DIR = Path(dirname(__file__)) / "data" / "wireguard"


def test_wireguard_cronitor():
    wg = WireguardMonitor(
        interfaces={
            "client1": str(WIREGUARD_CONFIG_DIR / "client1.conf"),
            "client2": str(WIREGUARD_CONFIG_DIR / "client2.conf"),
        }
    )
    assert wg.interfaces == [
        WireGuardInterface(
            interface_spec="client1", endpoint=EndPoint(host="localhost", port=8888)
        ),
        WireGuardInterface(
            interface_spec="client2", endpoint=EndPoint(host="localhost", port=51820)
        ),
    ]


def test_read_wg_status_server_and_client_config():
    output = (WIREGUARD_CONFIG_DIR / "wg-show-output1.txt").read_text()
    with patch("subprocess.run") as mock_subprocess_run:
        mock_subprocess_run.return_value = MagicMock(stdout=output)
        delta = WireguardMonitor.time_since_last_handshake(interface="wg-client")
        assert delta > 1000

import ipaddress
from os.path import dirname
from pathlib import Path
from unittest.mock import MagicMock, patch

from cronvisio.monitor.wireguard import (
    DEFAULT_TIMEOUT,
    EndPoint,
    WireGuardInterface,
    WireguardMonitor,
)

WIREGUARD_CONFIG_DIR = Path(dirname(__file__)) / "data" / "wireguard"


def test_wireguard_cronvisio():
    wg = WireguardMonitor(
        interfaces={
            "client1": str(WIREGUARD_CONFIG_DIR / "client1.conf"),
            "client2": str(WIREGUARD_CONFIG_DIR / "client2.conf"),
        }
    )
    assert wg.interfaces == [
        WireGuardInterface(
            interface_spec="client1",
            endpoint=EndPoint(
                host="localhost",
                port=8888,
                public_key="kEGKz8FXNlt/MR26o8ubQKT1shy+bHyQGQRLjmJxOXE=",
            ),
        ),
        WireGuardInterface(
            interface_spec="client2",
            endpoint=EndPoint(
                host="127.0.0.1",
                port=51820,
                public_key="cCfEsloNFf+bEwY/W87xI7L77H+ErlItnpICl2wjlEw=",
            ),
        ),
    ]


def test_read_wg_status_server_and_client_config():
    output = (WIREGUARD_CONFIG_DIR / "wg-show-output1.txt").read_text()
    with patch("subprocess.run") as mock_subprocess_run:
        mock_subprocess_run.return_value = MagicMock(stdout=output)
        delta = WireguardMonitor.time_since_last_handshake(interface="wg-client")
        assert delta > 1000


def test_resolve_host():
    # ip address
    assert WireguardMonitor.get_ipaddress("127.0.01") == "127.0.0.1"
    # Host
    assert ipaddress.ip_address(WireguardMonitor.get_ipaddress("weichselbraun.net"))


def test_notify_handshake_ok():
    with patch(
        "cronvisio.monitor.wireguard.WireguardMonitor.time_since_last_handshake"
    ) as mock_time_since_last_handshake:
        mock_time_since_last_handshake.return_value = DEFAULT_TIMEOUT - 1
        wg = WireguardMonitor(
            interfaces={
                ":client1": str(WIREGUARD_CONFIG_DIR / "client1.conf"),
                ":client2": str(WIREGUARD_CONFIG_DIR / "client2.conf"),
            }
        )
        assert wg.notify() == ""


def test_notify_handshake_delayed():
    with (
        patch(
            "cronvisio.monitor.wireguard.WireguardMonitor.time_since_last_handshake"
        ) as mock_time_since_last_handshake,
        patch("subprocess.run") as mock_subprocess_run,
    ):
        mock_time_since_last_handshake.return_value = DEFAULT_TIMEOUT + 1
        wg = WireguardMonitor(
            interfaces={
                ":client1": str(WIREGUARD_CONFIG_DIR / "client1.conf"),
                "ns2:client2": str(WIREGUARD_CONFIG_DIR / "client2.conf"),
            }
        )
        assert wg.notify() == (
            "Wireguard interface :client1 hasn't responded for 3 minutes.\n"
            "Critical: Reconnect to endpoint localhost:8888 failed.\n"
            "Wireguard interface ns2:client2 hasn't responded for 3 minutes.\n"
            "Critical: Reconnect to endpoint 127.0.0.1:51820 failed."
        )

        # Verify that subprocess.run has been called twice with the correct arguments
        expected_cmds = (
            "wg set client1 peer kEGKz8FXNlt/MR26o8ubQKT1shy+bHyQGQRLjmJxOXE= endpoint 127.0.0.1:8888",
            "ip netns exec ns2 wg set client2 peer cCfEsloNFf+bEwY/W87xI7L77H+ErlItnpICl2wjlEw= "
            "endpoint 127.0.0.1:51820",
        )
        for call_args, expected_cmd in zip(mock_subprocess_run.call_args_list, expected_cmds, strict=False):
            args, kwargs = call_args
            assert " ".join(args[0]) == expected_cmd
            assert kwargs["check"]
            assert kwargs["capture_output"]
            assert kwargs["text"]


def test_reconnect_to_wireguard_server():
    name = "wg0"
    namespace = ""
    public_key = "abcdef123456"
    host = "gateway.example.com"
    port = 51820

    with patch("subprocess.run") as mock_subprocess_run:
        # Call the function
        WireguardMonitor.reconnect_to_wireguard_server(name, namespace, public_key, host, port)

        # Verify subprocess.run() was called with the correct command line
        expected_cmd = (
            "wg",
            "set",
            name,
            "peer",
            public_key,
            "endpoint",
            f"{host}:{port}",
        )
        mock_subprocess_run.assert_called_once_with(expected_cmd, check=True, capture_output=True, text=True)


def test_reconnect_to_wireguard_server_with_namespace():
    name = "wg0"
    namespace = "test0"
    public_key = "abcdef123456"
    host = "gateway.example.com"
    port = 51820

    with patch("subprocess.run") as mock_subprocess_run:
        # Call the function
        WireguardMonitor.reconnect_to_wireguard_server(name, namespace, public_key, host, port)

        # Verify subprocess.run() was called with the correct command line
        expected_cmd = (
            "ip",
            "netns",
            "exec",
            namespace,
            "wg",
            "set",
            name,
            "peer",
            public_key,
            "endpoint",
            f"{host}:{port}",
        )
        mock_subprocess_run.assert_called_once_with(expected_cmd, check=True, capture_output=True, text=True)

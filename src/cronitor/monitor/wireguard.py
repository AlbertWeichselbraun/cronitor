#!/usr/bin/env python3
"""
Check and repair wireguard interfaces that have been frozen due to a change of the endpoint's IP address.

Logic:
- get a list of relevant interfaces + their corresponding config
- read the global wl interface status
- for each relevant interface;  check if a timeout occurred
  - no => return none
  - yes => try updating the endpoint ip, return an info on the update, if successful
           and a warning otherwise.
"""
import configparser
import ipaddress
import socket
import subprocess
from time import time
from typing import Optional, NamedTuple

from cronitor import Monitor

WL_HANDSHAKE = ["wg", "show", "all", "latest-handshakes"]
WL_CHANGE_ENDPOINT = ["wg", "set", "endpoint"]

DEFAULT_TIMEOUT = 150


class EndPoint(NamedTuple):
    host: str
    port: int


class WireGuardInterface(NamedTuple):
    interface_spec: str
    endpoint: EndPoint


class WireguardMonitor(Monitor):
    def __init__(self, interfaces: dict[str, str], timeout: int = DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.interfaces = [
            WireGuardInterface(
                interface_spec=interface_spec,
                endpoint=self.read_host_from_wl_config(interface_conf),
            )
            for interface_spec, interface_conf in interfaces.items()
        ]

    def notify(self, force: bool = True) -> str:
        """
        Check all configured wireguard interfaces and notify the user of frozen ones.
        """
        msg = []
        for interface_spec, endpoint in self.interfaces:
            namespace, name = interface_spec.split(":")
            if delta := self.time_since_last_handshake(name, namespace) > self.timeout:
                msg.append(
                    f"Wireguard interface {interface_spec} hasn't responded for"
                    f"{round(delta/60)} seconds."
                )
                if not endpoint:
                    msg.append("Cannot reconnect. No endpoint for interface specified.")
                self.reconnect_to_wireguard_server(name, namespace, endpoint)
                if self.time_since_last_handshake(name, namespace) > self.timeout:
                    msg.append(f"Critical: Reconnect to endpoint {endpoint} failed.")
                else:
                    msg.append(f"Successfully reconnected to endpoint {endpoint}.")
        return "\n".join(msg)

    @staticmethod
    def get_ipaddress(hostname: str) -> Optional[str]:
        """
        Return the IP address for the given hostname
        """
        try:
            ipaddress.ip_address(hostname)
            return hostname
        except ValueError:
            pass
        try:
            return socket.gethostbyname(hostname)
        except socket.error as e:
            print(f"Error: {e}")
            return None

    @staticmethod
    def reconnect_to_wireguard_server(
        name: str, namespace: str, endpoint: EndPoint
    ) -> None:
        pass

    @staticmethod
    def read_host_from_wl_config(config_filename: str) -> Optional[EndPoint]:
        """
        Determine the endpoints for all configured client wireguard interfaces.
        (i.e., only the interfaces that connect to an endpoint).

        Args:
             config_filename: path to wireguard configuration file.

        Returns:
            An Endpoint tuple which consists of the host and port of the endpoint.
        """
        config = configparser.ConfigParser()
        with open(config_filename) as f:
            config.read_file(f)
        try:
            host, port = config.get("Peer", "Endpoint").split(":")
            return EndPoint(host, int(port))
        except configparser.NoOptionError:
            return None

    @staticmethod
    def time_since_last_handshake(
        interface: str, namespace: Optional[str] = None
    ) -> float:
        """
        Determine the status of all wireguard connections on the given host.

        Example output:
        wg-de	KEY=	1708807507

        Returns:
            The time since last handshake'.
        """
        cmd = (
            WL_HANDSHAKE
            if not namespace
            else ["ip", "netns", "exec", namespace] + WL_HANDSHAKE
        )
        return next(
            (
                time() - float(timestamp)
                for line in subprocess.run(
                    cmd, check=True, capture_output=True, text=True
                ).stdout.split("\n")
                for iface, _, timestamp in [line.split()]
                if iface == interface
            ),
            None,
        )

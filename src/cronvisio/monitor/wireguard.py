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
from typing import NamedTuple

from cronvisio import Monitor

WL_HANDSHAKE = ("wg", "show", "all", "latest-handshakes")

DEFAULT_TIMEOUT = 150


class EndPoint(NamedTuple):
    host: str
    port: int
    public_key: str

    def __str__(self):
        return f"{self.host}:{self.port}"


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
            if (delta := self.time_since_last_handshake(name, namespace)) > self.timeout:
                msg.append(f"Wireguard interface {interface_spec} hasn't responded for {round(delta / 60)} minutes.")
                if not endpoint:
                    msg.append("Cannot reconnect. No endpoint for interface specified.")
                    continue
                self.reconnect_to_wireguard_server(
                    name,
                    namespace,
                    endpoint.public_key,
                    self.get_ipaddress(endpoint.host),
                    endpoint.port,
                )
                if self.time_since_last_handshake(name, namespace) > self.timeout:
                    msg.append(f"Critical: Reconnect to endpoint {endpoint} failed.")
                else:
                    msg.append(f"Successfully reconnected to endpoint {endpoint}.")
        return "\n".join(msg)

    @staticmethod
    def get_ipaddress(hostname: str) -> str | None:
        """
        Return the IP address for the given hostname
        """
        try:
            ipaddress.ip_address(hostname)
        except ValueError:
            pass
        else:
            return hostname

        try:
            return socket.gethostbyname(hostname)
        except OSError as e:
            print(f"Error: {e}")
            return None

    @staticmethod
    def reconnect_to_wireguard_server(name: str, namespace: str, public_key: str, host: str, port: int) -> None:
        cmd = ("wg", "set", name, "peer", public_key, "endpoint", f"{host}:{port}")
        if namespace:
            cmd = ("ip", "netns", "exec", namespace, *cmd)
        subprocess.run(cmd, check=True, capture_output=True, text=True)

    @staticmethod
    def read_host_from_wl_config(config_filename: str) -> EndPoint | None:
        """
        Determine the endpoints for all configured client wireguard interfaces.
        (i.e., only the interfaces that connect to an endpoint).

        Args:
             config_filename: path to wireguard configuration file.

        Returns:
            An Endpoint which consists of the host, port and public key of the endpoint.
        """
        config = configparser.ConfigParser()
        with open(config_filename) as f:
            config.read_file(f)
        try:
            host, port = config.get("Peer", "Endpoint").split(":")
            public_key = config.get("Peer", "PublicKey")
            return EndPoint(host, int(port), public_key)
        except configparser.NoOptionError:
            return None

    @staticmethod
    def time_since_last_handshake(interface: str, namespace: str | None = None) -> float:
        """
        Determine the status of all wireguard connections on the given host.

        Example output:
        wg-de	KEY=	1708807507

        Returns:
            The time since last handshake.
        """
        cmd = WL_HANDSHAKE if not namespace else ("ip", "netns", "exec", namespace, *WL_HANDSHAKE)
        return next(
            (
                time() - float(timestamp)
                for line in subprocess.run(cmd, check=True, capture_output=True, text=True).stdout.split("\n")
                for iface, _, timestamp in [line.split()]
                if iface == interface
            ),
            None,
        )

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import logging
import re
from time import sleep
import miniupnpc

import docker

# Set file path as current path
# os.chdir(os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger(__name__)


def init_log(use_file=False):
    """set logging"""
    formatter = logging.Formatter(
        "%(asctime)s %(filename)s %(levelname)s [line:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    handlers = [console]
    if use_file:
        logfile = logging.FileHandler(f"{os.path.splitext(__file__)[0]}.log")
        logfile.setFormatter(formatter)
        handlers.append(logfile)
    logging.basicConfig(level=logging.INFO, handlers=handlers)
    logger.setLevel(logging.DEBUG)


class DPortMap:
    def __init__(self):
        self.watch_all = os.environ.get("WATCH") == "ALL"
        if self.watch_all:
            logger.info('Watch all containers except label with "upnp.igd.enable=False"')
        else:
            logger.info('Only watch container with label "upnp.igd.enable=True"')
        self.client = docker.DockerClient(version="auto", timeout=50)
        self.upnp_client = UpnpClient()
        self.main()

    def get_ports(self, ports):
        all_ports = set()
        for internal_port, external_ports in ports.items():
            if external_ports:
                port_type = internal_port.split("/")[-1]
                for external_port in external_ports:
                    port = external_port.get("HostPort")
                    all_ports.add(f"{port_type}.{port}")
        return all_ports

    def get_conf(self, labels):
        """get conf from labels"""
        enabled_ports = set()
        disabled_ports = set()
        enable = self.watch_all
        for label, value in labels.items():
            if not label.startswith("upnp.igd."):
                continue
            label = label.replace("upnp.igd.", "")
            if value in ("false", "False"):
                value = False
            else:
                value = True
            if label == "enable":
                enable = value
                continue
            if value is False:
                disabled_ports.add(label)
            else:
                enabled_ports.add(label)
        return enable, enabled_ports, disabled_ports

    def main(self):
        for container in self.client.containers.list():
            # prefer use value of label "com.docker.compose.project" as name than use container name
            name = container.labels.get("com.docker.compose.project", container.name)
            enable, enabled_ports, disabled_ports = self.get_conf(container.labels)
            if not enable:
                logger.info(f"skip {name}")
                continue
            all_ports = self.get_ports(container.ports)
            needed_ports = (all_ports | enabled_ports) - disabled_ports
            if not needed_ports:
                logger.info(f"no port found in {name}")
                continue
            self.set_nat(name, needed_ports)
            print("-" * 79)

    def set_nat(self, name, ports):
        for i in ports:
            protocol, port = i.split(".")
            self.upnp_client.map_port(protocol, port, name)


class UpnpClientOld:
    def __init__(self, duration=4800):
        status = os.popen("upnpc -s").read()
        igd = re.findall("Found valid IGD : (.*)", status)
        if not igd:
            logger.warning("IGD not found.")
            return
        self.igd = igd[0]
        self.lan_ip = re.findall("Local LAN ip address : (.*)", status)[0]
        self.duration = duration

    def map_port(self, protocol, port, name):
        comment = ".".join([protocol, port, name])
        print(comment)
        cmd = f'upnpc -u {self.igd} -e "{comment}" -a {self.lan_ip} {port} {port} {protocol} {self.duration} | grep external'
        os.system(cmd)


class UpnpClient:
    def __init__(self):
        self.upnp = miniupnpc.UPnP()
        # self.duration = duration
        self.discover()

    def discover(self):
        self.upnp.discover()
        self.upnp.selectigd()

    def map_port(self, protocol, port, name):
        comment = ".".join([protocol, port, name])
        logger.info(comment)
        self.upnp.addportmapping(
            int(port), protocol, self.upnp.lanaddr, int(port), comment, ""
        )


def main():
    while True:
        DPortMap()
        logger.info("sleep 3600s")
        sleep(3600)
    # supported labels:
    # to-do: duration as env
    # env: interval 1h default


if __name__ == "__main__":
    init_log()
    main()

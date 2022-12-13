#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import logging

import docker

# Set file path as current path
os.chdir(os.path.dirname(os.path.abspath(__file__)))

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


class UpnpIgd:
    def __init__(self):
        self.client = docker.DockerClient(version="auto", timeout=50)
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
        enable = True
        for label, value in labels.items():
            if not label.startswith("upnp.igd."):
                continue
            label = label.replace("upnp.igd.", "")
            if value in ("false", "False"):
                value = False
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
            name = container.labels.get("com.docker.compose.project", container.name)
            enable, enabled_ports, disabled_ports = self.get_conf(container.labels)
            if not enable:
                logger.info(f"skip {name}")
                continue
            all_ports = self.get_ports(container.ports)
            needed_ports = (all_ports | enabled_ports) - disabled_ports
            if not needed_ports:
                logger.info(f"no port found in {name}")
            self.set_nat(name, needed_ports)
            print("-" * 79)

    def set_nat(self, name, ports):
        import re
        status = os.popen('upnpc -s').read()
        igd = re.findall('Found valid IGD : (.*)',status)
        if not igd:
            logger.warning('IGD not found.')
            return
        igd = igd[0]
        lan_ip = re.findall('Local LAN ip address : (.*)',status)[0]

        expires = 4800
        extra_paras = ''
        for i in ports:
            protocol, port = i.split(".")
            comment = ".".join([protocol, port, name])
            print(comment)
            # 'upnpc -s'
            cmd = f'upnpc -u {igd} -e "{comment}" -a {lan_ip} {port} {port} {protocol} {expires}'
            os.system(cmd)


def main():
    UpnpIgd()
    from time import sleep
    logger.info('sleep 3600s')
    sleep(3600)
    # supported labels:
    # upnp.igd.enable=False  # true if not mentioned
    # upnp.igd.tcp.17288=false
    # upnp.igd.udp.3333  # true can leave out
    # prefer use label "com.docker.compose.project" as name than container name
    # to-do: expires as env
    # read igd use 'upnpc -s' command
    # env: need enable first
    # env: interval 1h default

    # docker upnp portmapping
if __name__ == "__main__":
    init_log()
    main()

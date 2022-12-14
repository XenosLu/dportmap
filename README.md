

[![version](https://images.microbadger.com/badges/version/xenocider/dportmap.svg)](https://microbadger.com/images/xenocider/dportmap "Get your own version badge on microbadger.com")
[![](https://images.microbadger.com/badges/image/xenocider/dportmap.svg)](https://microbadger.com/images/xenocider/dportmap "Get your own image badge on microbadger.com")

[![Docker Pulls](https://img.shields.io/docker/pulls/xenocider/dportmap.svg)](https://hub.docker.com/r/xenocider/dportmap/ "Docker Pulls")
[![Docker Stars](https://img.shields.io/docker/stars/xenocider/dportmap.svg)](https://hub.docker.com/r/xenocider/dportmap/ "Docker Stars")

[![Auto Build Docker](https://github.com/XenosLu/dportmap/actions/workflows/main.yml/badge.svg)](https://github.com/XenosLu/dportmap/actions/workflows/main.yml)


# dportmap - docker auto port mapping through upnp IGD

# [中文](#chinese)  [English](#english)

# <span id="chinese">中文版</span>
## dportmap - 自动将docker容器的端口映射到IGD设备上（通常是家用路由器）
适用场景，单机docker需要将容器中的大多数端口映射至公网

docker-compose 样例
```
services:
  single:
    environment:
    - WATCH=ALL  # 该值为all时会监控所有容器除了包含label "upnp.igd.enable=False"的容器
    image: xenocider/dportmap:latest
    network_mode: host
    restart: always
    volumes:
    - /var/run/docker.sock:/var/run/docker.sock
version: '3'
```

启动该容器后将自动监控所有容器，并自动将容器的所有TCP/UDP端口映射到自动检测到的IGD设备上。
可通过对相关容器设置label来
支持的ENV参数：
WATCH=ALL  # 该值为all时会监控所有容器除了包含label "upnp.igd.enable=False"的容器
支持的标签(label)列表：
- upnp.igd.enable=False  # 如果值为空则认为true
- upnp.igd.tcp.7788=false
- upnp.igd.tcp.8080=true
- upnp.igd.udp.3333  # =true可以省略


---
# <span id="english">English Version</span>
## dportmap - 自动将docker容器的端口映射到IGD设备上（通常是家用路由器）
适用场景，单机docker需要将容器中的大多数端口映射至公网
docker-compose sample
```
services:
  single:
    environment:
    - WATCH=ALL  # will watch all container except with label "upnp.igd.enable=False"
    image: xenocider/dportmap:latest
    network_mode: host
    restart: always
    volumes:
    - /var/run/docker.sock:/var/run/docker.sock
version: '3'
```

Supported labels：
- upnp.igd.enable=False  # true if value is none
- upnp.igd.tcp.17288=false
- upnp.igd.udp.3333  # true can leave out
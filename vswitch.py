#!/usr/bin/env python3

import socket
import sys

if len(sys.argv) != 2:
    print("Usage: python3 vswitch.py {VSWITCH_PORT}")
    sys.exit(1)

server_port = int(sys.argv[1])
server_addr = ("0.0.0.0", server_port)

# create and bind UDP socket
vserver_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
vserver_sock.bind(server_addr)
print(f"[VSwitch] Started at {server_addr[0]}:{server_addr[1]}")

#  MAC -> (ip, port)
mac_table = {}

while True:
    data, vport_addr = vserver_sock.recvfrom(1518)

    # parse ethernet header
    eth_header = data[:14]
    eth_dst = ":".join(f"{x:02x}" for x in eth_header[0:6])
    eth_src = ":".join(f"{x:02x}" for x in eth_header[6:12])

    print(f"[VSwitch] vport_addr<{vport_addr}> src<{eth_src}> dst<{eth_dst}> datasz<{len(data)}>" )

    # learn/update source MAC
    if eth_src not in mac_table or mac_table[eth_src] != vport_addr:
        mac_table[eth_src] = vport_addr
        print(f"    ARP Cache: {mac_table}")

    # forwarding logic
    if eth_dst in mac_table:
        # unicast
        vserver_sock.sendto(data, mac_table[eth_dst])
        print(f"    Forwarded to: {eth_dst}")

    elif eth_dst == "ff:ff:ff:ff:ff:ff":
        # broadcast
        brd_macs = [mac for mac in mac_table if mac != eth_src]
        brd_addrs = {mac_table[mac] for mac in brd_macs}
        print(f"    Broadcasted to: {brd_addrs}")
        for addr in brd_addrs:
            vserver_sock.sendto(data, addr)

    elif eth_dst.startswith("01:00:5e") or eth_dst.startswith("33:33"):
        # multicast (IPv4 and IPv6)
        mcast_macs = [mac for mac in mac_table if mac != eth_src]
        mcast_addrs = {mac_table[mac] for mac in mcast_macs}
        print(f"    Multicast forwarded to: {mcast_addrs}")
        for addr in mcast_addrs:
            vserver_sock.sendto(data, addr)

    else:
        print(f"    Discarded")

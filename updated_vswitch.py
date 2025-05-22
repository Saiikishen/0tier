#!/usr/bin/env python3

import socket
import sys
import time

# parse parameters
if len(sys.argv) != 2:
    print("Usage: python3 vswitch.py {VSWITCH_PORT}")
    sys.exit(1)

server_port = int(sys.argv[1])
server_addr = ("0.0.0.0", server_port)

# create and bind UDP socket
vserver_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
vserver_sock.bind(server_addr)
print(f"[VSwitch] Started at {server_addr[0]}:{server_addr[1]}")

# MAC address table: maps MAC -> (ip, port)
mac_table = {}

def print_mac_table():
    """Print the MAC address table in a formatted way"""
    print("\n" + "="*70)
    print("                      MAC ADDRESS TABLE")
    print("="*70)
    if not mac_table:
        print("| No entries in MAC table                                    |")
    else:
        print("| MAC Address       | VPort Address      | Last Updated       |")
        print("|" + "-"*68 + "|")
        current_time = time.strftime("%H:%M:%S")
        for mac, vport_addr in mac_table.items():
            print(f"| {mac:<17} | {vport_addr[0]:<10}:{vport_addr[1]:<5} | {current_time:<18} |")
    print("="*70)
    print(f"Total entries: {len(mac_table)}")
    print()

frame_count = 0

while True:
    # read ethernet frame from VPort
    data, vport_addr = vserver_sock.recvfrom(1518)
    frame_count += 1

    # parse ethernet header
    eth_header = data[:14]
    eth_dst = ":".join(f"{x:02x}" for x in eth_header[0:6])
    eth_src = ":".join(f"{x:02x}" for x in eth_header[6:12])

    print(f"[VSwitch] Frame #{frame_count} - vport_addr<{vport_addr}> src<{eth_src}> dst<{eth_dst}> datasz<{len(data)}>" )

    # learn/update source MAC
    mac_updated = False
    if eth_src not in mac_table or mac_table[eth_src] != vport_addr:
        mac_table[eth_src] = vport_addr
        mac_updated = True
        print(f"    MAC Learning: {eth_src} -> {vport_addr}")

    # forwarding logic
    if eth_dst in mac_table:
        # unicast
        vserver_sock.sendto(data, mac_table[eth_dst])
        print(f"    Forwarded to: {eth_dst} at {mac_table[eth_dst]}")

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
        # unknown unicast or other
        print(f"    Discarded (unknown destination)")

    # Print MAC table every 5 frames or when MAC table is updated
    if mac_updated or frame_count % 5 == 0:
        print_mac_table()
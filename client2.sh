#!/bin/bash

# Variables
TAP_IF="cn_proj2"
IP_ADDR="10.0.0.2/24"
SERVER_IP="127.0.0.1"
SERVER_PORT="9993"

# Run vport in background
sudo ./vport $SERVER_IP $SERVER_PORT $TAP_IF &
sleep 1  # wait for TAP creation

# Configure TAP
sudo ip addr add $IP_ADDR dev $TAP_IF
sudo ip link set dev $TAP_IF up

echo "[Client 2] $TAP_IF is up with IP $IP_ADDR"


 ping 10.0.0.1

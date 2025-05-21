#!/bin/bash

sudo ip tuntap add dev cn_proj mode tap user $USER
sudo ip link set cn_proj up
sudo ip addr add 10.1.1.101/24 dev cn_proj

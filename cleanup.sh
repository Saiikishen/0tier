#!/bin/bash

echo "[*] Killing vport and vswitch processes..."
sudo pkill vport
sudo pkill vswitch

echo "[*] Deleting TAP interfaces..."
sudo ip link del cn_proj1 2>/dev/null && echo "Deleted cn_proj1" || echo "cn_proj1 not found"
sudo ip link del cn_proj2 2>/dev/null && echo "Deleted cn_proj2" || echo "cn_proj2 not found"

echo "[✓] Cleanup complete."

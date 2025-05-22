#!/bin/bash
# client1.sh - Enhanced Client 1 Script
# Variables
TAP_IF="cn_proj1"
IP_ADDR="10.0.0.1/24"
SERVER_IP="127.0.0.1"
SERVER_PORT="9993"
PEER_IP="10.0.0.2"

echo "[Client 1] Starting setup..."

# Check if VSwitch is running
echo "[Client 1] Checking if VSwitch is running on port $SERVER_PORT..."
if ! nc -z $SERVER_IP $SERVER_PORT 2>/dev/null; then
    echo "[Client 1] ERROR: VSwitch not running on $SERVER_IP:$SERVER_PORT"
    echo "[Client 1] Please start VSwitch first: python3 vswitch.py $SERVER_PORT"
    exit 1
fi

# Clean up any existing processes
echo "[Client 1] Cleaning up existing processes..."
sudo pkill -f "vport.*$TAP_IF" || true
sudo ip link delete $TAP_IF 2>/dev/null || true

# Start vport in background
echo "[Client 1] Starting vport..."
sudo ./vport $SERVER_IP $SERVER_PORT $TAP_IF &
VPORT_PID=$!

# Wait for TAP interface to be created
echo "[Client 1] Waiting for TAP interface creation..."
sleep 2

# Verify TAP interface exists
if ! ip link show $TAP_IF >/dev/null 2>&1; then
    echo "[Client 1] ERROR: TAP interface $TAP_IF not created"
    kill $VPORT_PID 2>/dev/null || true
    exit 1
fi

# Configure TAP interface
echo "[Client 1] Configuring TAP interface..."
sudo ip addr add $IP_ADDR dev $TAP_IF
sudo ip link set dev $TAP_IF up

# Verify interface is up and configured
sleep 1
if ip addr show $TAP_IF | grep -q "$IP_ADDR"; then
    echo "[Client 1] ✅ $TAP_IF is up with IP $IP_ADDR"
else
    echo "[Client 1] ERROR: Failed to configure $TAP_IF"
    kill $VPORT_PID 2>/dev/null || true
    exit 1
fi

# Wait for peer to be ready (coordination mechanism)
echo "[Client 1] Waiting for peer to be ready..."
echo "[Client 1] Will wait up to 30 seconds for peer at $PEER_IP..."

# Try to detect peer readiness by checking ARP/ping
PEER_READY=false
for i in {1..30}; do
    # Send a ping to help with ARP discovery
    if ping -c 1 -W 1 -I $TAP_IF $PEER_IP >/dev/null 2>&1; then
        PEER_READY=true
        echo "[Client 1] ✅ Peer detected and responding!"
        break
    fi
    echo "[Client 1] Waiting for peer... ($i/30)"
    sleep 1
done

if [ "$PEER_READY" = false ]; then
    echo "[Client 1] ⚠️  Peer not detected, but proceeding with ping test..."
fi

# Start ping test
echo "[Client 1] Starting ping test to $PEER_IP..."
echo "[Client 1] Press Ctrl+C to stop"
echo "----------------------------------------"

# Continuous ping with statistics
ping -I $TAP_IF $PEER_IP

# Cleanup on exit
cleanup() {
    echo -e "\n[Client 1] Cleaning up..."
    kill $VPORT_PID 2>/dev/null || true
    sudo ip link delete $TAP_IF 2>/dev/null || true
    echo "[Client 1] Cleanup complete"
}

trap cleanup EXIT

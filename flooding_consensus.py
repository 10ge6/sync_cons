#!/usr/bin/env python3

import sys
import socket
import time
import random

# Usage: python3 flooding_consensus.py <host_ip> <other_host_ips...>
# Example: python3 flooding_consensus.py 10.0.0.1 10.0.0.2 10.0.0.3

UDP_PORT = 9999
ROUNDS = 10
ROUND_DURATION = 1.0  # seconds between rounds

from datetime import datetime

def log_event(event_message):
    """Log events with timestamps including milliseconds."""
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Format with milliseconds
    print(f"[{timestamp}]: {event_message}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 flooding_consensus.py <my_ip> <peer_ip1> <peer_ip2> ...")
        sys.exit(1)
    
    my_ip = sys.argv[1]
    peers = sys.argv[2:]
    
    # Create a socket for receiving
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    recv_sock.bind((my_ip, UDP_PORT))
    recv_sock.setblocking(False)  # non-blocking
    
    # Initial value for consensus
    my_value = random.randint(0,100)
    known_values = {my_value}
    
    log_event(f"[{my_ip}] Starting consensus with initial value {my_value}")
    
    for r in range(ROUNDS):
        log_event(f"[{my_ip}] Starting round {r+1}")
        
        # Send known values to all peers
        message = ",".join(map(str, known_values)).encode('utf-8')
        send_start_time = time.time()
        if my_ip != "10.0.0.3" or r == 6:
            for p in peers:
                send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                send_sock.sendto(message, (p, UDP_PORT))
                send_sock.close()
        log_event(f"[{my_ip}] Finished sending information to peers in {time.time() - send_start_time:.4f} seconds")
        
        # Wait to receive values from peers during this round
        start_time = time.time()
        while time.time() - start_time < ROUND_DURATION:
            try:
                data, addr = recv_sock.recvfrom(4096)
                arrival_time = time.time()
                vals = data.decode('utf-8').split(',')
                log_event(f"[{my_ip}] Received data from {addr[0]} at {arrival_time:.4f}: {vals}")
                for v in vals:
                    known_values.add(int(v))
            except BlockingIOError:
                time.sleep(0.01)
        
        log_event(f"[{my_ip}] Ended round {r+1} after {time.time() - start_time:.4f} seconds. Known values: {known_values}")
    
    # After ROUNDS, decide on the consensus value
    consensus_value = min(known_values)
    log_event(f"[{my_ip}] Consensus reached: {consensus_value}")

if __name__ == "__main__":
    main()

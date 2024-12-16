#!/usr/bin/env python3

import sys
import socket
import time
import random
import threading
from datetime import datetime
import json
import threading

# Usage: python3 flooding_consensus.py <host_ip> <peer_ip1> <peer_ip2> ... 
# Example: python3 flooding_consensus.py 10.0.0.1 10.0.0.2 10.0.0.3

UDP_PORT = 9999
ROUNDS = 5
ROUND_DURATION = 1  # seconds between rounds
LOCK = threading.Lock()  # Lock to synchronize access to shared data
DROPRATE = 0

def log_event(event_message):
    """Log events with timestamps including milliseconds."""
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Format with milliseconds
    print(f"[{timestamp}]: {event_message}")


class FloodingNode:
    def __init__(self, my_ip, peers):
        self.my_ip = my_ip
        self.peers = peers
        self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.recv_sock.bind((my_ip, UDP_PORT))
        self.recv_sock.setblocking(False)
        
        self.known_values = set([int(my_ip[-1])])  # Initial value
        self.values_to_send = set(self.known_values)  # Values to send at the start of the round
        self.running = True

        # Metrics
        self.messages_sent = 0
        self.messages_received = 0
        self.messages_lost = 0
        self.execution_start_time = None
        self.execution_end_time = None
        
    def send_thread(self):
        """Thread for sending data to peers."""
        self.execution_start_time = time.time()  # Record start time

        for r in range(ROUNDS):
            
            log_event(f"[{self.my_ip}] Starting round {r+1}, current known_values {self.known_values}")
            
            # Lock to freeze values to send at the start of the round
            with LOCK:
                self.values_to_send = set(self.known_values)  # Freeze known values at round start
            
            message = ",".join(map(str, self.values_to_send)).encode('utf-8')
            send_start_time = time.time()
            
            for p in self.peers:
                if random.uniform(0, 1) < DROPRATE:
                    self.messages_lost += 1
                    log_event(f"ROUND {r+1} [{self.my_ip}] message to [{p}] failed")
                    continue
                send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                send_sock.sendto(message, (p, UDP_PORT))
                send_sock.close()
                self.messages_sent += 1
                log_event(f"ROUND {r+1} [{self.my_ip}] message sent to [{p}] successfully: {message}")
            duration = time.time() - send_start_time
            log_event(f"[{self.my_ip}] Finished sending information in round {r+1} after {duration:.4f} seconds")
            time.sleep(max(0, ROUND_DURATION - duration))  # Ensure round duration is respected

        self.execution_end_time = time.time()  # Record end time
 

    def receive_thread(self):
        while self.running:
            try:
                data, addr = self.recv_sock.recvfrom(4096)
                with LOCK:
                    # Process late messages
                    vals = data.decode('utf-8').split(',')
                    new_values = []
                    for v in vals:
                        if int(v) not in self.known_values:
                            self.known_values.add(int(v))
                            new_values.append(v)

                self.messages_received += 1
                log_event(
                f"[{self.my_ip}] Received data from {addr[0]} at {time.time():.4f}: {vals}. "
                f"New values added: {new_values if new_values else 'None'}"
            )

            except BlockingIOError:
                time.sleep(0.01)

    def stop(self):
        """Stop the node by shutting down the receive thread."""
        self.running = False
        self.recv_sock.close()


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 flooding_consensus.py <my_ip> <peer_ip1> <peer_ip2> ...")
        sys.exit(1)
    
    my_ip = sys.argv[1]
    peers = sys.argv[2:]
    
    # Initialize the FloodingNode
    node = FloodingNode(my_ip, peers)
    
    # Start the receive and send threads
    receive_thread = threading.Thread(target=node.receive_thread, daemon=True)
    send_thread = threading.Thread(target=node.send_thread, daemon=True)
    
    receive_thread.start()
    send_thread.start()
    
    # Wait for the send thread to finish all rounds
    send_thread.join()
    
    # Stop the receive thread
    node.stop()
    receive_thread.join()
    
    # Determine the consensus value
    consensus_value = min(node.known_values)
    log_event(f"[{my_ip}] Consensus reached: {consensus_value}")
    
    # Calculate execution duration
    execution_duration = node.execution_end_time - node.execution_start_time

    # Create JSON metrics
    metrics = {
        "node_ip": my_ip,
        "consensus_value": consensus_value,
        "messages_sent": node.messages_sent,
        "messages_received": node.messages_received,
        "messages_lost": node.messages_lost,
        "execution_duration": round(execution_duration, 4),
        "known_values": list(node.known_values),
    }

    # Log final metrics as JSON
    metrics_json = json.dumps(metrics)
    #metrics_json = json.dumps(metrics, indent=4)
    log_event(f"[{my_ip}] Final Metrics:\n{metrics_json}")


if __name__ == "__main__":
    main()


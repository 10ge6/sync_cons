#!/usr/bin/env python3

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import OVSController
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.term import makeTerms
from mininet.link import TCLink  
import time
import os
from mininet.topo import Topo
import json

class SimpleTopo(Topo):

    def build(self):
        # Add a switch
        switch1 = self.addSwitch('s1')

        # Add hosts
        h1 = self.addHost('h1', ip='10.0.0.1')
        h2 = self.addHost('h2', ip='10.0.0.2')
        h3 = self.addHost('h3', ip='10.0.0.3')
        h4 = self.addHost('h4', ip='10.0.0.4')
        h5 = self.addHost('h5', ip='10.0.0.5')
        h6 = self.addHost('h6', ip='10.0.0.6')


        # Add links with realistic delays
        self.addLink(h1, switch1, delay='10ms', cls=TCLink)  
        self.addLink(h2, switch1, delay='10ms', cls=TCLink)  
        self.addLink(h3, switch1, delay='10ms', cls=TCLink)
        self.addLink(h4, switch1, delay='10ms', cls=TCLink)
        self.addLink(h5, switch1, delay='10ms', cls=TCLink)   
        self.addLink(h6, switch1, delay='10ms', cls=TCLink)

def read_logs_and_collect_json(directory='log'):

    result_list = []

    # Check if the directory exists
    if not os.path.exists(directory):
        print(f"Directory '{directory}' does not exist.")
        return result_list

    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        
        # Process only files
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r') as file:
                    # Attempt to parse the file content as JSON
                    lines = file.readlines()
                    last_line = lines[-1].strip()
                    
                    content = file.read().strip()
                    if last_line:  # Ensure file is not empty
                        try:
                            json_data = json.loads(last_line)  # Parse JSON
                            result_list.append(json_data)
                        except json.JSONDecodeError:
                            print(f"File {filename} does not contain valid JSON. Skipping.")
            except Exception as e:
                print(f"Error reading file {filename}: {e}")

    return result_list

if __name__ == '__main__':
    setLogLevel('info')
    topo = SimpleTopo()
    net = Mininet(topo=topo, controller=OVSController)
    net.start()

    info('*** Starting flooding consensus algorithm on all hosts\n')

    # Collect host information for the consensus script
    hosts = net.hosts
    all_ips = [host.IP() for host in hosts]

    #makeTerms(hosts, term='xterm')
    #time.sleep(2)
    
    # Start the flooding consensus script on each host
    dict_cmd_messages = {}
    for host in hosts:
        other_ips = [ip for ip in all_ips if ip != host.IP()]
        cmd = f"python3 flooding_consensus.py {host.IP()} {' '.join(other_ips)} > log/{host.name}_output.log 2>&1 &"
        dict_cmd_messages[host.IP()] = cmd
        
    for host in hosts:
        host.cmd(dict_cmd_messages[host.IP()])

    info('*** Flooding consensus algorithm started on all hosts\n')
    time.sleep(7)

    net.stop()
    
    json_metrics_list = read_logs_and_collect_json()
    
    consensus_set = []
    mensagens_enviadas = 0
    mensagens_recebidas = 0
    mensagens_perdidas = 0
    
    for metric_dict in json_metrics_list:
        consensus_set.append(metric_dict["consensus_value"])
        mensagens_enviadas += metric_dict["messages_sent"]
        mensagens_enviadas += metric_dict["messages_lost"]
        mensagens_perdidas += metric_dict["messages_lost"]
        mensagens_recebidas += metric_dict["messages_received"]
        
    print(f"Consenso atingido: {len(set(consensus_set)) == 1} \nGrupo de consenso: {set(consensus_set)} \nNúmero de mensagens enviadas: {mensagens_enviadas} \nNúmero de mensagens perdidas: {mensagens_perdidas}\nNúmero de mensagens recebidas: {mensagens_recebidas}")
    
    

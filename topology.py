#!/usr/bin/env python3

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import OVSController
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.term import makeTerms
import time

class SimpleTopo(Topo):
    """
    A simple topology:
      h1 --- s1 --- h2
             |
             h3
    (You can modify this as needed.)
    """
    def build(self):
        hostlist = []
        switch = self.addSwitch('s1')
        
        for 
        h1 = self.addHost('h1', ip='10.0.0.1')
        h2 = self.addHost('h2', ip='10.0.0.2')
        h3 = self.addHost('h3', ip='10.0.0.3')
        # Add links
        self.addLink(h1, switch)
        self.addLink(h2, switch)
        self.addLink(h3, switch)

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
    for host in hosts:
        other_ips = [ip for ip in all_ips if ip != host.IP()]
        cmd = f"python3 flooding_consensus.py {host.IP()} {' '.join(other_ips)} > log/{host.name}_output.log 2>&1 &"
        info(f"Starting on {host.name}: {cmd}\n")
        host.cmd(cmd)
        time.sleep(0.1)  # Optional delay to stagger the start of the scripts

    info('*** Flooding consensus algorithm started on all hosts\n')

    # Keep Mininet running to observe the network
 

    net.stop()


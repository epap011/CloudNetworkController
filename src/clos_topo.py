#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import irange,dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import RemoteController

import argparse
import sys
import time

class ClosTopo(Topo):

    core_level_switches_list      = []
    aggregate_level_switches_list = []
    edge_level_switches_list      = []
    host_level_switches_list      = []

    def __init__(self, fanout, cores, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)
       
        "Set up Core and Aggregate level, Connection Core - Aggregation level"
        for i in range(cores):
            self.core_level_switches_list.append(self.addSwitch('core'+str(i+1)))

        for i in range(cores*fanout):
            self.aggregate_level_switches_list.append(self.addSwitch('aggr'+str(cores+i+1)))
        
        for core_switch in self.core_level_switches_list:
            for aggr_switch in self.aggregate_level_switches_list:
                self.addLink(core_switch, aggr_switch)

        "Set up Edge level, Connection Aggregation - Edge level "
        for i in range(cores*fanout*fanout):
            self.edge_level_switches_list.append(self.addSwitch('edge'+str(cores*fanout+cores+i+1)))
        
        for aggr_switch in self.aggregate_level_switches_list:
            for edge_switch in self.edge_level_switches_list:
                self.addLink(aggr_switch, edge_switch)
        
        "Set up Host level, Connection Edge - Host level "
        for i in range(cores*fanout*fanout*fanout):
            self.host_level_switches_list.append(self.addHost('h'+str(i+1)))

        counter = 0
        for edge in range(len(self.edge_level_switches_list)):
            self.addLink(self.edge_level_switches_list[edge], self.host_level_switches_list[counter])
            counter = counter + 1
            self.addLink(self.edge_level_switches_list[edge], self.host_level_switches_list[counter])
            counter = counter + 1

def setup_clos_topo(fanout=2, cores=1):
    "Create and test a simple clos network"
    assert(fanout>0)
    assert(cores>0)
    topo = ClosTopo(fanout, cores)
    net = Mininet(topo=topo, controller=lambda name: RemoteController('c0', "127.0.0.1"), autoSetMacs=True, link=TCLink)
    net.start()
    time.sleep(20) #wait 20 sec for routing to converge
    net.pingAll()  #test all to all ping and learn the ARP info over this process
    CLI(net)       #invoke the mininet CLI to test your own commands
    net.stop()     #stop the emulation (in practice Ctrl-C from the CLI 
                   #and then sudo mn -c will be performed by programmer)

    
def main(argv):
    parser = argparse.ArgumentParser(description="Parse input information for mininet Clos network")
    parser.add_argument('--num_of_core_switches', '-c', dest='cores', type=int, help='number of core switches')
    parser.add_argument('--fanout', '-f', dest='fanout', type=int, help='network fanout')
    args = parser.parse_args(argv)
    setLogLevel('info')
    setup_clos_topo(args.fanout, args.cores)


if __name__ == '__main__':
    main(sys.argv[1:])
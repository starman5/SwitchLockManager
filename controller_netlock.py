#! /usr/bin/python3

# ./controller/controller_fattree_l3.py
#   Insert P4 table entries to route traffic among hosts for FatTree topology
#   under L3 routing

from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
import sys
import math

class RoutingController(object):

    def __init__(self):
        self.topo = load_topo("topology.json")
        self.controllers = {}
        self.init()

    def init(self):
        self.connect_to_switches()
        self.reset_states()
        self.set_table_defaults()

    def connect_to_switches(self):
        for p4switch in self.topo.get_p4switches():
            thrift_port = self.topo.get_thrift_port(p4switch)
            self.controllers[p4switch] = SimpleSwitchThriftAPI(thrift_port)

    def reset_states(self):
        [controller.reset_state() for controller in self.controllers.values()]

    def set_table_defaults(self):
        # TODO: define table default actions
        for controller in self.controllers.values():
            controller.table_set_default("ipv4_lpm", "NoAction", [])

    def route(self):
        for sw_name, controller in self.controllers.items():

            # Core switches
            if sw_name[0] == "c":
                    for host_id in range(1, host_num + 1):
                        out_port = int(math.ceil(host_id / (half_k ** 2)))
                        controller.table_add("ipv4_lpm", "set_nhop", ["10.0.0.%d/32" % (host_id,)], ["%d" % (out_port,)])

            # Aggregate switches
            elif sw_name[0] == "a":
                group = 2
                # Add mappings from (hash, group) -> out_port
                for hash_val in range(half_k * half_k * 10):
                    new_out = ((hash_val // group) % half_k) + 1
                    controller.table_add("ecmp_group_to_nhop", "set_nhop", [str(hash_val), str(group)], ["%d" % (new_out,)])
                
                sw_num = int(sw_name[1::])
                my_pod_idx = int(math.ceil(sw_num / half_k)) - 1
                for host_id in range(1, host_num + 1):
                    dest_pod_idx = int(math.ceil(host_id / (half_k ** 2))) - 1
                    # If going up tree, invoke ecmp logic
                    if my_pod_idx != dest_pod_idx:
                        controller.table_add("ipv4_lpm", "ecmp_group", ["10.0.0.%d/32" % (host_id,)], [str(group), str(k // 2)])
                    # If going down the tree, just set next hop and skip ecmp logic
                    else:
                        dest_pod_firsthost = ((half_k ** 2) * dest_pod_idx) + 1
                        out_port = math.ceil((host_id - dest_pod_firsthost + 1) / half_k) + half_k
                        controller.table_add("ipv4_lpm", "set_nhop", ["10.0.0.%d/32" % (host_id,)], ["%d" % (out_port,)])
            
            # TOR switches   
            elif sw_name[0] == "t":
                group = 1
                # Add mappings from (hash, group) -> out_port
                for hash_val in range(half_k * half_k * 10):
                    new_out = ((hash_val // group) % half_k) + 1 + half_k
                    controller.table_add("ecmp_group_to_nhop", "set_nhop", [str(hash_val), str(group)], ["%d" % (new_out,)])

                sw_num = int(sw_name[1:])
                for host_id in range(1, host_num + 1):
                    dest_tor_idx = int(math.ceil(host_id / half_k)) - 1
                    if dest_tor_idx != sw_num - 1:
                        # If going up the tree, add ecmp_group action to ipv4_lpm table
                        controller.table_add("ipv4_lpm", "ecmp_group", ["10.0.0.%d/32" % (host_id,)], [str(group), str(k // 2)])
                    else:
                        # If going down the tree, just set next hop, skip ecmp logic
                        out_port = host_id % half_k
                        if out_port == 0:
                            out_port = half_k

                        controller.table_add("ipv4_lpm", "set_nhop", ["10.0.0.%d/32" % (host_id,)], ["%d" % (out_port,)])


            '''if sw_name == "s2" or sw_name == "s3":
                dst_sw_mac_h2 = self.topo.node_to_node_mac("s4", sw_name)
                dst_sw_mac_h1 = self.topo.node_to_node_mac("s1", sw_name)
                controller.table_add("ipv4_lpm", "set_nhop", [str(self.topo.get_host_ip("h2") + "/32")], [str(dst_sw_mac_h2), "2"])
                controller.table_add("ipv4_lpm", "set_nhop", [str(self.topo.get_host_ip("h1") + "/32")], [str(dst_sw_mac_h1), "1"])

            elif sw_name == "s1":
                group = 1
                for hash_val in range(2 * 2 * 10):
                    # new_out is either 2 or 3
                    new_out = ((hash_val // group) % 2) + 2
                    if new_out == 2:
                        dst_sw_mac = self.topo.node_to_node_mac("s1", "s2")
                    else:
                        dst_sw_mac = self.topo.node_to_node_mac("s1", "s3")
                    controller.table_add("ecmp_group_to_nhop", "set_nhop", [str(hash_val), str(group)], [str(dst_sw_mac), "%d" % (new_out,)])
                
                controller.table_add("ipv4_lpm", "ecmp_group", [str(self.topo.get_host_ip("h2") + "/32")], [str(group), "2"])
                controller.table_add("ipv4_lpm", "set_nhop", [str(self.topo.get_host_ip("h1") + "/32")], [str(self.topo.get_host_mac("h1")), "1"])

            else:
                group = 2
                for hash_val in range(2 * 2 * 10):
                    # new_out is either 1 or 2
                    new_out = ((hash_val // group) % 2) + 1
                    if new_out == 1:
                        dst_sw_mac = self.topo.node_to_node_mac("s4", "s2")
                    else:
                        dst_sw_mac = self.topo.node_to_node_mac("s4", "s3")
                    controller.table_add("ecmp_group_to_nhop", "set_nhop", [str(hash_val), str(group)], [str(dst_sw_mac), "%d" % (new_out,)])
                
                controller.table_add("ipv4_lpm", "ecmp_group", [str(self.topo.get_host_ip("h1") + "/32")], [str(group), "2"])
            
                controller.table_add("ipv4_lpm", "set_nhop", [str(self.topo.get_host_ip("h2") + "/32")], [str(self.topo.get_host_mac("h2")), "3"])

            '''

    def main(self):
        self.route()


if __name__ == "__main__":
    controller = RoutingController().main()
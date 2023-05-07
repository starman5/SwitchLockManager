from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI

class RoutingController(object):

    def __init__(self):

        self.topo = load_topo("topology.json")
        self.controllers = {}
        self.init()

    def init(self):
        self.connect_to_switches()
        self.reset_states()
        self.set_table_defaults()

    def reset_states(self):
        [controller.reset_state() for controller in self.controllers.values()]

    def connect_to_switches(self):
        for p4switch in self.topo.get_p4switches():
            thrift_port = self.topo.get_thrift_port(p4switch)
            self.controllers[p4switch] = SimpleSwitchThriftAPI(thrift_port)

    def set_table_defaults(self):
        for controller in self.controllers.values():
            controller.table_set_default("ipv4_lpm", "drop", [])

    
    def route(self):
        for sw_name, controller in self.controllers.items():
            controller.table_add("ipv4_lpm", "set_nhop", ["10.1.1.2/32"], ["00:00:0a:01:01:02", "1"])
            controller.table_add("ipv4_lpm", "set_nhop", ["10.1.2.2/32"], ["00:00:0a:01:02:02", "2"])
            controller.table_add("ipv4_lpm", "set_nhop", ["10.1.3.2/32"], ["00:00:0a:01:03:02", "3"])

    
    def main(self):
        self.route()


if __name__ == "__main__":
    controller = RoutingController().main()

import sys
import os

from scapy.all import sniff, get_if_list, Ether, get_if_hwaddr, IP, Raw, Packet, BitField, bind_layers

ACQUIRE = 0
RELEASE = 1

class ResponseHeader(Packet):
    """
    The response header sent back to the 
    """

    #BitField(name, default_size, size)
    fields_desc=[
        BitField("lock_id", 0, 16)
        BitField("action", 0, 1),
        BitField("client_ip", 0, 32)
    ]

def get_if():
    iface = None
    for i in scapy.get_if_list():
        if "eth0" in i:
            iface = i
            break
        if not iface:
            print("Cannot find eth0 interface")
            exit(1)
        return iface
    
def isNotOutgoing(my_mac):
    my_mac = my_mac
    def _isNotOutoging(pkt):
        return pkt[Ether].src != my_mac
    return _isNotOutgoing


def handle_pkt(pkt):

    ether = pkt.getlayer(Ether)
    udp = pkt.getlayer(UDP)
    print("source port:", udp.sport)

def main():
    ifaces = list(filter(lamda i: 'eth' in i, os.listdir(''/sys/class/net/'')))
    iface = ifaces[0]
    print("sniffing on %s" % iface)
    sys.stdout.flush()

    my_filter = isNotOutgoing(get_if_hwaddr(get_if))

    sniff(filter="ether proto ")


if __name__ == '__main__':
    main()

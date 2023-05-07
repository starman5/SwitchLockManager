"""
The receiver listens for messages coming from UDP 7777.  This UDP is set aside for netlock.
All messages from netlock to host are indications that the lock has been granted.  If netlock
cannot grant the lock to the host, it just won't send a message back until it can grant the lock.
So we listen for messages from UDP 7777 and interpret those as messages that we have acquired
the lock we have requested.
"""

import sys
import os

from scapy.all import sniff, get_if_list, Ether, get_if_hwaddr, IP, UDP, Raw, Packet, BitField, bind_layers

def get_if():
    iface = None
    for i in get_if_list():
        if "eth0" in i:
            iface = i
            break
    if not iface:
        print("Cannot find eth0")
        exit(1)
    return iface


def isNotOutgoing(my_mac):
    my_mac = my_mac
    def _isNotOutgoing(pkt):
        return pkt[Ether].src != my_mac

    return _isNotOutgoing

def handle_pkt(pkt):
    udp = pkt.getlayer(UDP)
    if udp and udp.sport == 7777:
        print("acquired lock")

def main():
    ifaces = list(filter(lambda i: 'eth' in i, os.listdir('/sys/class/net/')))
    iface = ifaces[0]
    print("snifffing on %s" % iface)
    sys.stdout.flush()

    my_filter = isNotOutgoing(get_if_hwaddr(get_if()))

    sniff(iface=iface, prn=lambda x: handle_pkt(x), lfilter=my_filter)

if __name__ == '__main__':
        main()

"""
This client sends a packet to acquire the lock.
"""

import argparse
import sys
import socket
import random
import struct

from scapy.all import sendp, get_if_list, get_if_hwaddr, get_if_addr, Ether, IP, UDP, TCP, Packet, BitField
import time

ACQUIRE = 0

class LockHeader(Packet):
    """
    The lock header used by the client to request a lock
    """

    #BitField(name, default_size, size)
    fields_desc=[
        BitField("lock_id", 0, 14),
        BitField("action", 0, 2)
    ]


def get_if():
    """
    Get the interface eth0
    If no interface has a name with "eth0", then exit program
    """

    iface=None
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    else:
        return iface



def main():

    if len(sys.argv) < 2:
        print("more args")
        exit(1)

    srcaddr = socket.gethostbyname(sys.argv[1])
    dstaddr = socket.gethostbyname(sys.argv[2])
    iface = get_if()
    pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=0x7777) / LockHeader(lock_id=0, action=ACQUIRE)
    pkt = pkt / IP(src=srcaddr, dst=dstaddr) / UDP(dport=7777, sport=random.randint(2000,65535))
    sendp(pkt, iface=iface, verbose=False)

if __name__ == '__main__':
    main()
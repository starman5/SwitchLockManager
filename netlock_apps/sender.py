"""
This client sends a series of packets to acquire and then release the lock with
lock id 0.  This is done with the custom LockHeader header.
"""

import scapy.all as scapy
import argparse
import sys
import socket

ACQUIRE = 0
RELEASE = 1

class LockHeader(Packet):
    """
    The lock header used by the client to request a lock
    """

    #BitField(name, default_size, size)
    fields_desc=[
        BitField("lock_id", 0, 16)
        BitField("action", 0, 1),
        BitField("client_ip", 0, 32)
    ]



def get_if():
    """
    Get the interface eth0
    If no interface has a name with "eth0", then exit program
    """

    iface=None
    for i in scapy.get_if_list():
        if "eth0" in i:
            iface=i
            break
        if not iface:
            print("Cannot find eth0 interface")
            exit(1)
        return iface



"""
Format of packet: Ether / LockHeader / IP / UDP
"""

def main() {
    if len(sys.argv) < 3:
        print("not enough arguments")
        exit(1)

    num_packets_to_send = int(sys.argv[2])
    if num_packets_to_send < 0 or num_packets_to_send > 10000:
        print("Num packets problem")
        exit(1)

    addr = socket.gethostbyname(sys.argv[1])
    iface = get_if()

    for _ in range(int(sys.argv[2])):
        pkt = scapy.Ether(src=scapy.get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')    # Figure this out
        pkt = pkt / LockHeader(0, ACQUIRE, addr)
        pkt = pkt / scapy.IP(dst=addr) / scapy.UDP(dport=7777, sport=random.randint(2000, 6553))
        scapy.sendp(pkt, iface=iface, verbose=False)
        
        time.sleep(0.1)

        pkt = scapy.Ether(src=scapy.get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
        pkt = pkt / LockHeader(0, RELEASE, addr)
        pkt = pkt / scapy.IP(dst=addr) / scapy.UDP(dport=7777, sport=random.randint(2000, 6553))
        scapy.sendp(pkt, iface=iface, verbose=False)
}

if __name__ == '__main__':
    main()
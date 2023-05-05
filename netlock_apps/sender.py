"""
This client sends a series of packets to acquire and then release the lock with
lock id 0.  This is done with the custom LockHeader header.
"""

import scapy.all as scapy

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


"""
Format of packet: Ether / LockHeader / IP / UDP
"""

def main() {
    for _ in range(int(sys.argv[2])):
        pkt = Ether()    # Figure this out
        pkt = pkt / LockHeader(0, ACQUIRE, addr)
        sendp(pkt, iface=iface, verbose=False)
        
        time.sleep(0.1)

        pkt = Ether() / LockHeader(0, RELEASE, addr)
        sendp(pkt, iface=iface, verbose=False)
}

if __name__ == '__main__':
    main()
import scapy.all as scapy

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

def handle_pkt(pkt):
    """
    Parse returned packets from switch
    """

    ether = pkt.getlayer(Ether)

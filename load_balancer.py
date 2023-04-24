from scapy.all import *

VIP = ""
server_ips = []

def sniffPackets(packet):
	# TODO
	# if a packet is destined for the VIP, then pick a destination server via hash. Next, encapsulate and send the packet.
	pass


def main():
	# TODO
	# choose an appropriate packet filter for the load balancer
	sniff(filter="", prn=sniffPackets)


if __name__ == "__main__":
	main()

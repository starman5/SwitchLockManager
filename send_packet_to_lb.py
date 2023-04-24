from scapy.all import *

VIP = "20.0.0.1"

def main():
	to_server = Ether() / \
				IP(dst=VIP) / \
				TCP()
	sendp(to_server)

if __name__ == "__main__":
	main()
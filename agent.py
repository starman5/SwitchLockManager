from scapy.all import *

def LB_to_server(packet):
	# TODO
  # extract the inner IP header from encapsulated packet and send to the server
  # before make sure to run this line: conf.L3socket = L3RawSocket
  # that command is required in order to speak to local applications like the server
  pass
  
def main():
	# TODO
  # write an appropriate packet filter for the host agent
	sniff(filter="",prn=LB_to_server)


if __name__ == "__main__":
	main()

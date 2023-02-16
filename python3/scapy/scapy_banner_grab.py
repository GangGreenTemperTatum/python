# In this script, we first define the IP address and port number of the target host, and then use Scapy to craft a TCP SYN packet and send it to the target host. We capture the response packet (a TCP SYN-ACK packet), and use its sequence and acknowledgement numbers to craft a TCP ACK packet. We then send this ACK packet to the target host and capture the response packet (which should be the HTTP response from the target service).
# If we receive a response packet, we extract the banner (i.e. the contents of the HTTP response) from its payload and print it to the console. If we don't receive a response packet at any point, we print an appropriate error message.

#!/usr/bin/env python

from scapy.all import *

# IP address of the target host
target_ip = "httpforever.com/"

# Port number of the service to grab banner from
target_port = 80

# Craft the TCP SYN packet
syn_packet = IP(dst=target_ip)/TCP(dport=target_port, flags="S")

# Send the SYN packet and capture the response
syn_ack_packet = sr1(syn_packet, timeout=5)

if syn_ack_packet:
    # Craft the TCP ACK packet
    ack_packet = IP(dst=target_ip)/TCP(dport=target_port, flags="A", seq=syn_ack_packet.ack, ack=syn_ack_packet.seq + 1)

    # Send the ACK packet and capture the response
    response_packet = sr1(ack_packet/TCP(dport=target_port, flags="F"), timeout=5)

    if response_packet:
        # Extract the banner from the response packet's payload (the HTTP response)
        banner = response_packet.load

        # Print the banner
        print(f"Banner: {banner}")
    else:
        print("No response received to ACK packet")
else:
    print("No response received to SYN packet")

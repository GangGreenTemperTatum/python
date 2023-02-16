import scapy.layers.l2 as scapy
def scan(ip): 
    scapy.arping(ip) 
scan('192.168.1.0/24') 

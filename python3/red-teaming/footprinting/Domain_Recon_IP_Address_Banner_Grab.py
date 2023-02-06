# This script takes the domain name as a command line argument, performs a lookup for its IP address using socket.gethostbyname, creates a socket and connects to the server using the IP address and port 80 (HTTP), sends an HTTP request to the server using send, receives the server's response using recv, decodes the banner and stores the results in a dictionary. The dictionary is then converted to a JSON string using json.dumps and printed.
# I recommend "piping" (|) the output with JQ to print the results in Pretty JSON, as by default will be NDJSON

import socket
import sys
import json

# Get the domain name
domain = sys.argv[1]

# Get the IP address of the domain
ip = socket.gethostbyname(domain)

# Create a socket and connect to the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((ip, 80))

# Send a request to the server
s.send(b"GET / HTTP/1.0\r\n\r\n")

# Receive the banner
banner = s.recv(1024)

# Create a dictionary to store the results
results = {
    "domain": domain,
    "ip": ip,
    "banner": banner.decode('utf-8')
}

# Convert the dictionary to a JSON string
json_str = json.dumps(results)

# Print the results
print(json_str)

# Close the socket
s.close()

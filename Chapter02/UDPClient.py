import socket

target_host = "127.0.0.1"
target_port = 9997

# Create a socket object
# AF_INET parameter for standard IPv4 address
# SOCK_DGRAM for UDP
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send some data as bytes
client.sendto(b"AAABBBCCC", (target_host,target_port))

# Receive data and details of remote host & port
data, addr = client.recvfrom(4096)

print(data.decode())
client.close()
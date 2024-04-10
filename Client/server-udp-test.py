import socket
import time
import struct


def run():
    # Define the UDP broadcast address and port
    UDP_IP = "255.255.255.255"  # Broadcast address
    UDP_PORT = 13117

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to the UDP address and port
    sock.bind(('', UDP_PORT))

    # Set socket to broadcast mode
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Broadcast message
    MESSAGE = construct_offer_packet("MyServer", 1232)

    print("Broadcasting UDP message...")
    while True:
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
        time.sleep(1)


# Function to construct the offer packet
def construct_offer_packet(server_name, server_port):
    magic_cookie = 0xabcddcba
    message_type = 0x2
    server_name_bytes = server_name.ljust(32).encode('utf-8')
    offer_packet = struct.pack('!IB32sH', magic_cookie, message_type, server_name_bytes, server_port)
    return offer_packet


run()

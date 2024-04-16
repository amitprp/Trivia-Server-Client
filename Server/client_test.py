import socket
import struct

from Client.client_exceptions import WrongMessageTypeError, WrongMagicCookieError

SERVER_IP = '192.168.1.220'
TCP_PORT = 54574

def main():
    try:

        # Create a UDP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Bind the socket to the port
        client_socket.bind(('0.0.0.0', 0))

        # Enable broadcasting on the socket
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # Create a TCP socket and connect to the server
        # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data, addr = client_socket.recvfrom(1024)  # Buffer size is 1024 bytes
        server_NAME, server_PORT = parse_offer_packet(data)
        print(server_NAME, server_PORT)
        client_socket.connect((SERVER_IP, server_PORT))

        # Send a message to the server
        player_name = "Alice"  # Change this to the desired player name
        client_socket.send(player_name.encode('utf-8'))
        print(f"Sent player name: {player_name}")

        # Receive a response from the server (optional)
        response = client_socket.recv(1024).decode('utf-8')
        print("Response from server:", response)

        # Close the socket
        client_socket.close()
    except ConnectionRefusedError:
        print("Failed to connect to the server. Make sure the server is running.")

def parse_offer_packet(offer):
    magic_cookie, message_type, server_name_bytes, server_port = struct.unpack('!IB32sH', offer)
    magic_hex = hex(magic_cookie)
    type_hex = hex(message_type)
    if magic_hex == '0xabcddcba':
        if type_hex == '0x2':
            server_name = server_name_bytes.decode('utf-8').strip()
            return server_name, server_port
        else:
            raise WrongMessageTypeError(f"{message_type} is not a supported message type!")
    else:
        raise WrongMagicCookieError(f"{magic_cookie} is not a supported starting magic cookie! Offer not accepted")


if __name__ == "__main__":
    main()
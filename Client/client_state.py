import socket
import struct
import time
from abc import abstractmethod
from client_exceptions import *


class ClientState:
    def __init__(self, client):
        self.client = client
        self.server_IP = None
        self.server_PORT = None

    @abstractmethod
    def handle(self):
        pass


class LookingForServerState(ClientState):

    def handle(self):
        # Define the UDP port to listen on
        UDP_PORT = 13117

        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Set socket options to allow receiving broadcast messages
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # Bind the socket to the UDP port
        sock.bind(('0.0.0.0', UDP_PORT))

        print("Listening for UDP broadcast messages...")

        try:
            data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
            server_NAME, server_PORT = self.parse_offer_packet(data)
            return True, server_NAME, addr, server_PORT
        except socket.error as e:
            print(f"Socket error occurred: {e}")
            return False, None, None, None
        except Exception as e:
            print(e)
            return False, None, None, None

    def parse_offer_packet(self, offer):
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


class ConnectingToServerState(ClientState):

    def __init__(self, server_IP, server_PORT, server_NAME, player_name):
        super().__init__(self)
        self.server_IP = server_IP
        self.server_PORT = server_PORT
        self.server_NAME = server_NAME
        self.player_name = player_name

    def handle(self):
        while True:
            # Create a TCP socket
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect to the server
            client_socket.connect((self.server_IP, self.server_PORT))

            # Now you can send and receive data using the client_socket
            # For example, you can send data to the server
            data = f"{self.player_name}\n"
            data_encoded = data.encode('utf-8')
            client_socket.send(data_encoded)

            # Receive data from the server
            data = client_socket.recv(1024)  # Receive up to 1024 bytes of data
            print("Received from server:", data.decode())

            # Close the connection
            client_socket.close()


    # Example usage:


class GameModeState(ClientState):
    def handle(self):
        # Code to handle game mode state
        pass

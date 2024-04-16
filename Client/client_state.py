import socket
import struct
import threading

from inputimeout import inputimeout, TimeoutOccurred
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
        # run on standard port range
        for UDP_PORT in range(49152, 65535):

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
                print(server_NAME, server_PORT)
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
            data = f"{self.player_name}\n".encode('utf-8')
            try:
                client_socket.send(data)
            except OSError:
                return False, None
            return True, client_socket

    # Example usage:


class GameModeState(ClientState):
    def __init__(self, server_CONNECTION):
        super().__init__(self)
        self.socket = server_CONNECTION
        self.input_interrupt = False
        self.input = None
        self.server_data = None

    def handle(self):
        # Code to handle game mode state
        try:
            self.receive_data_from_server()
            while
            self.input_interrupt = False
            input_thread = threading.Thread(target=self.check_input)
            data_thread = threading.Thread(target=self.receive_data_from_server)

            input_thread.start()
            data_thread.start()

            input_thread.join()
            data_thread.join()

        except OSError:
            print

    def check_input(self):
        print("Enter your answer: (Y,T,1 for yes/ N,F,0 for no)")
        self.input = None
        seconds = 10
        while not self.input_interrupt and seconds != 0:
            try:
                self.input = inputimeout(timeout=1)
                self.socket.sendall(self.input.encode('utf-8'))
            except TimeoutOccurred:
                seconds -= 1

    def receive_data_from_server(self):
        # Receive data from the server
        data = self.socket.recv(1024)  # Receive up to 1024 bytes of data
        self.input_interrupt = True
        print(data.decode())





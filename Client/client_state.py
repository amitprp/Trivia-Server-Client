import socket
import struct
import threading
from abc import abstractmethod
from client_exceptions import *
from Client import ReadJson


json_handle = ReadJson.JsonHandle('ClientJsons')
constants = json_handle.read_json('constants.json')
# Define the UDP port to listen on
UDP_PORT = constants['UDP_PORT']


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

        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Set socket options to allow receiving broadcast messages
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # Bind the socket to the UDP port
        sock.bind(('', UDP_PORT))

        print("Listening for UDP broadcast messages...")

        try:
            data, address = sock.recvfrom(1024)  # Buffer size is 1024 bytes
            server_NAME, server_PORT = self.parse_offer_packet(data)
            print(server_NAME, server_PORT)
            return True, server_NAME, address[0], server_PORT
        except socket.error as e:
            print(f"Socket error occurred: {e}")
            return False, None, None, None
        except Exception as e:
            print(e)
            return False, None, None, None

    @staticmethod
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


class GameModeState(ClientState):

    def __init__(self, server_SOCKET):
        super().__init__(self)
        self.socket = server_SOCKET


    def handle(self):
        while True:

            data = self.socket.recv(1024)
            if data:
                data_decoded = data.decode()
                print(data_decoded)
                # if data_decoded.startswith('Question'):
                try:
                    user_input = self.get_input_with_timeout(timeout=1).encode('utf-8')
                    self.socket.send(user_input)
                except InputTimeout:
                    pass
            else:
                print("Server closed the connection.")
                return


    def get_input_with_timeout(self, timeout):
        print(end='', flush=True)

        user_input = ['']  # A list to store user input

        def input_thread(my_socket):
            try:
                user_input[0] = input().encode('utf-8')  # Get user input
                my_socket.send(user_input[0])
            except OSError as e:
                print(e)

        input_thread = threading.Thread(target=input_thread, args=[self.socket])
        input_thread.start()

        input_thread.join(timeout)  # Wait for the input thread to finish or timeout
        if input_thread.is_alive():  # If the input thread is still alive after timeout
            raise InputTimeout

        return user_input[0]  # Return the user input

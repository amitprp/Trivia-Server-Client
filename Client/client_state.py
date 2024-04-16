import socket
import struct
import threading
from abc import abstractmethod
from client_exceptions import *
from Client import ReadJson
from inputimeout import inputimeout, TimeoutOccurred

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
        sock.bind(('0.0.0.0', UDP_PORT))

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

    def __init__(self, server_CONNECTION):
        super().__init__(self)
        self.socket = server_CONNECTION
        self.stop_listen_to_client = False

    def handle(self):
        # Code to handle game mode state
        while True:
            self.listen_to_server()
            self.listen_to_client()
        # listen_server_thread = threading.Thread(target=self.listen_to_server())
        # listen_server_thread.start()
        # user_input_thread = threading.Thread(target=self.listen_to_client())
        # user_input_thread.start()



    @staticmethod
    def get_input(k):
        """
        Get input from the user with a timeout.
        Displays the prompt to the user and waits for input for a maximum of 10 seconds.
        If no input is received within the timeout period, returns None.

        Returns:
            str or None: The input provided by the user or None if no input is received within the timeout.
        """
        answer = None
        try:
            answer = inputimeout(prompt=k, timeout=10)
        except TimeoutOccurred:
            pass
        return answer

    def listen_to_client(self):

        user_input = ''
        try:
            user_input = self.get_input("kobi 11")
            print(user_input)
        except EOFError:
            # Handle unexpected EOF, possibly by informing the user or taking other actions
            print("Unexpected EOF while reading input.")
        # Now you can send and receive data using the client_socket
        data = f"{user_input}\n".encode('utf-8')
        try:
            self.socket.send(data)
        except OSError as e:
            print(e)
        except ConnectionRefusedError:
            print("Connection refused: The server is not running or is unreachable")


    def listen_to_server(self):

        try:
            # Receive data from the server
            data = self.socket.recv(1024)  # Receive up to 1024 bytes of data
            print(data.decode())

        except TimeoutError:
            print("Connection timed out: The server did not respond within the specified timeout, trying again...")
        except OSError:
            self.stop_listen_to_client = True
        except ConnectionRefusedError:
            print("Connection refused: The server is not running or is unreachable")
            self.stop_listen_to_client = True

import socket
import psutil


def is_None(to_check, word):
    if to_check is None:
        print(f'there is no available {word} right now, try again later')
        exit(0)


class Network:

    def __init__(self):

        self.udp_port = self.find_available_port(False)
        is_None(self.udp_port, 'port')
        self.tcp_port = self.find_available_port(True)
        is_None(self.tcp_port, 'port')

        self.server_ip, self.subnet_mask = '192.168.1.220', '255.255.255.0'  # self.get_wireless_ip_address()
        is_None(self.server_ip, 'network')
        is_None(self.subnet_mask, 'network')

        self.udp_socket = self.create_udp_socket()
        is_None(self.udp_socket, 'socket')
        self.tcp_socket = self.create_tcp_socket()
        is_None(self.tcp_socket, 'socket')


    def get_udp_port(self):
        return self.udp_port

    def get_tcp_port(self):
        return self.tcp_port

    def get_tcp_socket(self):
        return self.tcp_socket

    def get_udp_socket(self):
        return self.udp_socket

    def get_ip_address(self):
        return self.server_ip


    def create_tcp_socket(self):

        try:
            # Create TCP socket for accepting client connections
            tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_server_socket.bind((self.server_ip, self.tcp_port))
            tcp_server_socket.listen()
            return tcp_server_socket
        except socket.error as e:
            print(f"Socket error: {e}")
            # Handle the error gracefully, possibly by retrying, logging, or exiting the program
            return None



    def create_udp_socket(self):

        try:
            # Create UDP socket for broadcasting offer announcements
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            server_socket.bind((self.server_ip, self.udp_port))
            return server_socket
        except socket.error as e:
            print(f"Socket error: {e}")
            # Handle the error gracefully, possibly by retrying, logging, or exiting the program
            return None


    def calc_broadcast_ip(self):
        # Calculate the broadcast IP address
        return self.calculate_broadcast_ip(self.server_ip, self.subnet_mask)


    def find_available_port(self, tcp_or_udp):

        start_port = 49152
        end_port = 65535

        for port in range(start_port, end_port + 1):

            if tcp_or_udp and port == self.udp_port:
                continue

            sock = None
            try:
                # Create a UDP socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                # Try binding to the current port
                sock.bind(('localhost', port))
                # If successful, return the port
                print(f'port {port} is free to use.')
                return port
            except OSError:
                # Port is already in use, try the next one
                pass
            finally:
                # Close the socket
                sock.close()

        # If no available port is found
        return None


    @staticmethod
    def get_wireless_ip_address():
        interfaces = psutil.net_if_addrs()
        statuses = psutil.net_if_stats()

        for interface_name, interface_addresses in interfaces.items():

            for address in interface_addresses:
                if address.family == socket.AF_INET and statuses[interface_name].isup:

                    ip_address = address.address
                    subnet_mask = address.netmask
                    print(ip_address, subnet_mask)
                    return ip_address, subnet_mask
        print("Cannot get wireless IP address")
        return None, None


    @staticmethod
    def calculate_broadcast_ip(ip_address, subnet_mask):
        # Calculate the broadcast IP address
        try:
            ip_parts = list(map(int, ip_address.split('.')))
            mask_parts = list(map(int, subnet_mask.split('.')))
            broadcast_parts = [(ip_parts[i] | (~mask_parts[i] & 0xff)) for i in range(4)]
            return '.'.join(map(str, broadcast_parts))
        except ValueError:
            return None


    @staticmethod
    def send_message(client_socket, message):
        try:
            if client_socket.fileno() != -1:
                client_socket.sendall(message.encode('utf-8'))
                print(message)
        except socket.error as e:
            print(f"Socket error: {e}")
        except UnicodeEncodeError as e:
            print(f"Unicode error: {e}")

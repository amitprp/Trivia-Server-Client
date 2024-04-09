import threading
import time
import random
import socket
import struct
import ipaddress


INTERFACE_NAME = '192.168.1.220'
UDP_PORT = 13117
TCP_PORT = 54574
BUFFER_SIZE = 1024
MAGIC_COOKIE = 0xabcddcba
MESSAGE_TYPE = 0x2
TIME_OUT_IN_SEC = 10

# List of trivia questions about NBA
nba_questions = [
    {"question": "Michael Jordan won six NBA championships with the Chicago Bulls.", "is_true": True},
    {"question": "The Los Angeles Lakers have won the most NBA championships in history.", "is_true": True},
    {"question": "LeBron James has won the NBA Most Valuable Player (MVP) award five times.", "is_true": True},
    {"question": "The Golden State Warriors set the record for most wins in an NBA regular season with 73 wins.", "is_true": True},
    {"question": "Kobe Bryant scored 100 points in a single NBA game.", "is_true": False},
    {"question": "The NBA was founded in 1950.", "is_true": False},
    {"question": "Larry Bird played his entire NBA career with the Boston Celtics.", "is_true": True},
    {"question": "The NBA Slam Dunk Contest was first held in 1976.", "is_true": True},
    {"question": "The NBA three-point line was introduced in the 1980s.", "is_true": False},
    {"question": "Shaquille O'Neal was known for his exceptional three-point shooting.", "is_true": False}
]

# List of trivia questions about surfing
surfing_questions = [
    {"question": "Kelly Slater is considered one of the greatest surfers of all time.", "is_true": True},
    {"question": "Surfing originated in Australia.", "is_true": False},
    {"question": "The biggest wave ever surfed measured over 100 feet tall.", "is_true": True},
    {"question": "A 'barrel' in surfing refers to a surfing competition.", "is_true": False},
    {"question": "Surfing made its Olympic debut at the 2020 Tokyo Olympics.", "is_true": True},
    {"question": "Hawaii is known as the birthplace of modern surfing.", "is_true": True},
    {"question": "A 'wipeout' in surfing refers to a successful ride on a wave.", "is_true": False},
    {"question": "Surfboards were originally made from aluminum.", "is_true": False},
    {"question": "The term 'hang ten' refers to riding a wave with all ten toes hanging over the edge of the surfboard.", "is_true": True},
    {"question": "Surfing was first practiced by ancient Polynesians.", "is_true": True}
]

ALL_QUESTIONS = nba_questions + surfing_questions


def get_ip_address(interface):
    # Get the IP address of the specified interface
    try:
        ip_address = socket.getaddrinfo(interface, None, socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_IP)[0][4][0]
        return str(ip_address)
    except OSError:
        return None


def get_subnet_mask(ip_address):
    try:
        ip_network = ipaddress.ip_interface(ip_address)
        subnet_mask_length = ip_network.network.prefixlen
        subnet_mask = ipaddress.IPv4Network('0.0.0.0/' + str(subnet_mask_length)).netmask
        return str(subnet_mask)
    except (ValueError, AttributeError):
        return None


def calculate_broadcast_ip(ip_address, subnet_mask):
    # Calculate the broadcast IP address
    try:
        ip_parts = list(map(int, ip_address.split('.')))
        mask_parts = list(map(int, subnet_mask.split('.')))
        broadcast_parts = [(ip_parts[i] | (~mask_parts[i] & 0xff)) for i in range(4)]
        return '.'.join(map(str, broadcast_parts))
    except ValueError:
        return None


SERVER_IP = get_ip_address(INTERFACE_NAME)
print(SERVER_IP)


def create_tcp_socket():
    # Create TCP socket for accepting client connections
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server_socket.bind((SERVER_IP, TCP_PORT))
    tcp_server_socket.listen()
    return tcp_server_socket


def create_udp_socket():

    # Create UDP socket for broadcasting offer announcements
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server_socket.bind((SERVER_IP, UDP_PORT))
    return server_socket


def check_answer(answer, correct_answer):

    return answer == correct_answer



def calc_broadcast_ip(interface):

    ip_address = get_ip_address(interface)
    subnet_mask = get_subnet_mask(interface)
    print(ip_address, subnet_mask)

    # Calculate the broadcast IP address
    return calculate_broadcast_ip(ip_address, subnet_mask)


class Server:


    def __init__(self, name):
        self.name = name
        self.UDP_socket = create_udp_socket()
        self.TCP_socket = create_tcp_socket()
        self.clients = []
        # self.ip_address = get_ip_address(INTERFACE_NAME)
        self.timer = 0
        self.timer_lock = threading.Lock()
        self.clients_lock = threading.Lock()
        self.answers = []
        self.answers_lock = threading.Lock()


    def send_offer_broadcast(self, message, broadcast):

        while self.timer < TIME_OUT_IN_SEC:
            self.UDP_socket.sendto(message, (broadcast, UDP_PORT))
            print(message)
            print("Offer broadcasted")
            self.add_to_timer()
            time.sleep(1)


    def handle_client(self, client_sock, client_add):

        print(f"Connection from {client_add}")
        player_name = client_sock.recv(1024).decode('utf-8').strip()
        print(f"Received player name: {player_name}")
        player_tup = (client_sock, client_add, player_name)
        self.add_to_locked_list(player_tup, self.clients_lock)


    def add_to_locked_list(self, player, my_lock):
        my_lock.acquire()
        try:
            self.clients.append(player)
        finally:
            my_lock.release()


    def accept_clients(self):

        self.TCP_socket.settimeout(TIME_OUT_IN_SEC)

        # Accept client connections for the specified duration
        while True:
            try:
                client_socket, client_address = self.TCP_socket.accept()
                print("Accepted connection from:", client_address)
                self.reset_timer()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.start()
            except socket.timeout:
                print("Timeout reached. No more clients will be accepted.")
                break


    def add_to_timer(self):
        self.timer_lock.acquire()
        try:
            self.timer += 1
        finally:
            self.timer_lock.release()


    def reset_timer(self):
        self.timer_lock.acquire()
        try:
            self.timer = 0
        finally:
            self.timer_lock.release()


    def construct_offer_packet(self):

        server_name_bytes = self.name.ljust(32).encode('utf-8')
        offer_packet = struct.pack('!IB32sH', MAGIC_COOKIE, MESSAGE_TYPE, server_name_bytes, TCP_PORT)
        return offer_packet


    def get_answer(self, client_socket, player_name):

        client_socket.settimeout(TIME_OUT_IN_SEC)

        try:

            player_ans = client_socket.recv(BUFFER_SIZE)
            str_player_ans = player_ans.decode('utf-8')
            player_tup = (player_name, str_player_ans)
            self.add_to_locked_list(player_tup, self.answers_lock)

        except socket.timeout:
            print("Timeout reached. No more clients will be accepted.")
        except Exception as e:
            print("An error occurred while receiving data from the client:", e)


    def check_answers(self, correct_ans):
        for ans in self.answers:
            if check_answer(ans[1], correct_ans):
                return True
        return False


    def start_game(self):

        no_winner = True
        index = 0
        random.shuffle(ALL_QUESTIONS)

        while no_winner:
            message = ALL_QUESTIONS[index]["question"]
            correct_ans = ALL_QUESTIONS[index]["is_true"]
            threads = []
            for client_socket, client_address, player_name in self.clients:
                try:
                    client_socket.sendall(message.encode('utf-8'))
                    ans_thread = threading.Thread(target=self.get_answer, args=(client_socket, player_name))
                    ans_thread.start()
                    threads.append(ans_thread)
                    print("Message sent to client at:", client_address)
                except Exception as e:
                    print("Failed to send message to client at:", client_address, "Error:", e)

            # TODO check if we got good answer

            for thread in threads:
                thread.join()

            if not self.check_answers(correct_ans):
                continue



            index += 1








    def manage_game(self):

        print(f"Server started, listening on IP address {SERVER_IP}")
        offer_message = self.construct_offer_packet()
        broadcast_ip = calc_broadcast_ip(INTERFACE_NAME)
        # Start broadcasting offer announcements in a separate thread
        offer_thread = threading.Thread(target=self.send_offer_broadcast, args=(offer_message, broadcast_ip))
        offer_thread.start()
        self.accept_clients()

        self.start_game()


if __name__ == "__main__":
    s = Server("kobiz")
    s.manage_game()

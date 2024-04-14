import threading
import time
import random
import socket
import struct
import psutil

# ANSI reset
RESET = "\033[0m"

# ANSI escape codes for formatting
BOLD = "\033[1m"

# ANSI escape codes for background colors
PALE_BLUE_BACKGROUND = "\033[104m"
BACKGROUND_BLUE = "\033[44m"
BACKGROUND_YELLOW = "\033[43m"
PURPLE_BACKGROUND = "\033[45m"
RED_BACKGROUND = "\033[41m"
WHITE_BACKGROUND = "\033[107m"
ORANGE_BACKGROUND = "\033[48;2;255;165;0m"
CYAN_BACKGROUND = "\033[46m"

# ANSI escape codes for colors
RED_TEXT = "\033[91m"
GREEN_TEXT = "\033[92m"
YELLOW_TEXT = "\033[93m"
WHITE_TEXT = "\033[97m"
BLACK_TEXT = "\033[30m"

# history data
GOT_IT_RIGHT = 'right answers'
Q_ANSWERED = 'question answered'
Q_ASKED = 'question asked'
GAME_PLAYED = 'games played'
WINS = 'wins'
STATISTICS_DICT = {Q_ASKED: 0, GOT_IT_RIGHT: 0, Q_ANSWERED: 0, GAME_PLAYED: 0, WINS: 0}

# default messages
RIGHT_ANSWER = 'You showed great knowledge you must be a pro!'
WRONG_ANSWER = 'Wrong answer maybe next time.'
INVALID_ANSWER = 'Answer have to be one of the following: y, t, 1 for True or n, f, 0 for False'
NO_ANSWER = 'Ohh you missed it, You have to answer faster!'
NO_GOOD_ANSWERS = 'You can do better. 0/20 really!?'
END_OF_GAME = 'Thank you for playing, hope to see you soon! :)'
WELCOME_MESSAGE = 'Welcome to our NBA and Surfing quiz.\nYou better be right if you want to win!'

# constants
BUFFER_SIZE = 1024
MAGIC_COOKIE = 0xabcddcba
MESSAGE_TYPE = 0x2
TIME_OUT_IN_SEC = 10

# interface wifi names
WIFI_INTERFACE_NAMES = [
    # Linux
    "wlan0", "wlan1", "wlan2",
    # Newer Predictable Network Interface Names
    "wlpXsY",
    # macOS
    "Wi-Fi",
    # Windows
    "Wi-Fi", "Wireless Network Connection", "WLAN",
    # BSD
    "wlan0", "wlan1", "wlan2"
]

# possible answers
POSSIBLE_TRUE_ANSWERS = ['y', 't', '1']
POSSIBLE_FALSE_ANSWERS = ['0', 'n', 'f']


def find_available_port(tcp_or_udp):

    start_port = 49152
    end_port = 65535

    for port in range(start_port, end_port + 1):
        if tcp_or_udp and UDP_PORT == port:
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


# ports for thw whole session
UDP_PORT = find_available_port(False)
TCP_PORT = find_available_port(True)


# List of trivia questions about NBA
nba_questions = [
    {"question": RED_BACKGROUND + BLACK_TEXT + "Michael Jordan won six NBA championships with the Chicago Bulls." + RESET, "is_true": True},
    {"question": PURPLE_BACKGROUND + YELLOW_TEXT + "The Los Angeles Lakers have won the most NBA championships in history." + RESET, "is_true": True},
    {"question": RED_BACKGROUND + WHITE_TEXT + "LeBron James has won the NBA Most Valuable Player (MVP) award five times." + RESET, "is_true": True},
    {"question": BACKGROUND_BLUE + YELLOW_TEXT + "The Golden State Warriors set the record for most wins in an NBA regular season with 73 wins." + RESET, "is_true": True},
    {"question": PURPLE_BACKGROUND + YELLOW_TEXT + "Kobe Bryant scored 100 points in a single NBA game." + RESET, "is_true": False},
    {"question": ORANGE_BACKGROUND + BLACK_TEXT + "The NBA was founded in 1950." + RESET, "is_true": False},
    {"question": WHITE_BACKGROUND + GREEN_TEXT + "Larry Bird played his entire NBA career with the Boston Celtics." + RESET, "is_true": True},
    {"question": ORANGE_BACKGROUND + BLACK_TEXT + "The NBA Slam Dunk Contest was first held in 1976." + RESET, "is_true": True},
    {"question": ORANGE_BACKGROUND + BLACK_TEXT + "The NBA three-point line was introduced in the 1980s." + RESET, "is_true": False},
    {"question": PURPLE_BACKGROUND + YELLOW_TEXT + "Shaquille O'Neal was known for his exceptional three-point shooting." + RESET, "is_true": False}
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


def format_surfing_questions():
    for q in surfing_questions:
        q['question'] = CYAN_BACKGROUND + '~~~' + q['question'] + '~~~' + RESET


# all question formatted
format_surfing_questions()
ALL_QUESTIONS = nba_questions + surfing_questions


def get_wireless_ip_address():
    interfaces = psutil.net_if_addrs()
    for interface_name, interface_addresses in interfaces.items():
        cleaned_name = interface_name.replace("\u200F\u200F", "")
        for interface in WIFI_INTERFACE_NAMES:
            if cleaned_name.startswith(interface):
                for address in interface_addresses:
                    if address.family == socket.AF_INET:
                        ip_address = address.address
                        subnet_mask = address.netmask
                        return ip_address, subnet_mask
    print("Cannot get wireless IP address")
    return None, None


def calculate_broadcast_ip(ip_address, subnet_mask):
    # Calculate the broadcast IP address
    try:
        ip_parts = list(map(int, ip_address.split('.')))
        mask_parts = list(map(int, subnet_mask.split('.')))
        broadcast_parts = [(ip_parts[i] | (~mask_parts[i] & 0xff)) for i in range(4)]
        return '.'.join(map(str, broadcast_parts))
    except ValueError:
        return None


# ip and subnet-mask for the current computer
SERVER_IP, SUBNET_MASK = get_wireless_ip_address()
if not SERVER_IP or not SUBNET_MASK:
    print('There is no available wifi network, try again later')
    exit(0)


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


def calc_broadcast_ip():

    # Calculate the broadcast IP address
    return calculate_broadcast_ip(SERVER_IP, SUBNET_MASK)


def add_to_locked_list(player, my_lock, list_to_add):
    my_lock.acquire()
    try:
        list_to_add.append(player)
    finally:
        my_lock.release()


def send_message(client_socket, message):
    client_socket.sendall(message.encode('utf-8'))
    print(message)


def get_bool_ans(str_player_ans):
    lower_ans = str_player_ans.lower()
    if lower_ans in POSSIBLE_TRUE_ANSWERS:
        return True
    elif lower_ans in POSSIBLE_FALSE_ANSWERS:
        return False
    return None


class Server:


    def __init__(self, name):
        self.name = name
        self.UDP_socket = create_udp_socket()
        self.TCP_socket = create_tcp_socket()
        self.clients = []
        self.timer = 0
        self.timer_lock = threading.Lock()
        self.clients_lock = threading.Lock()
        self.answers = []
        self.answers_lock = threading.Lock()
        self.have_winner_lock = threading.Lock()
        self.have_winner = []
        self.history = ServerHistory()
        self.manage_game()

    def send_offer_broadcast(self, message, broadcast):

        while self.timer < TIME_OUT_IN_SEC:
            self.UDP_socket.sendto(message, (broadcast, UDP_PORT))
            print(message)
            print("Offer broadcast")
            self.add_to_timer()
            time.sleep(1)


    def handle_client(self, client_sock, client_add):

        print(f"Connection from {client_add}")
        player_name = client_sock.recv(1024).decode('utf-8').strip()
        print(f"Received player name: {player_name}")
        player_tup = (client_sock, client_add, player_name)
        self.history.add_to_history(player_name, GAME_PLAYED, 1)
        add_to_locked_list(player_tup, self.clients_lock, self.clients)

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

        if len(self.clients) == 0:
            print('There is no players right now!')
            exit(0)



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


    def get_answer(self, client_socket, player_name, correct_ans):

        client_socket.settimeout(TIME_OUT_IN_SEC)

        try:

            player_ans = client_socket.recv(BUFFER_SIZE)
            str_player_ans = player_ans.decode('utf-8')
            answer = get_bool_ans(str_player_ans)

            if check_answer(answer, correct_ans):
                player = (player_name, client_socket)
                add_to_locked_list(player, self.have_winner_lock, self.have_winner)
                self.history.add_to_history(player_name, Q_ANSWERED, 1)
                self.history.add_to_history(player_name, RIGHT_ANSWER, 1)
                send_message(client_socket, RIGHT_ANSWER)
            elif answer is None:
                send_message(client_socket, INVALID_ANSWER)
            else:
                send_message(client_socket, WRONG_ANSWER)
                self.history.add_to_history(player_name, Q_ANSWERED, 1)

        except socket.timeout:
            print("Timeout reached. No more clients will be accepted.")
            send_message(client_socket, NO_ANSWER)
        except Exception as e:
            print("An error occurred while receiving data from the client:", e)


    def start_game(self):

        index = 0
        random.shuffle(ALL_QUESTIONS)

        while len(self.have_winner) == 0 and index < len(ALL_QUESTIONS):

            message = f'Question {index+1}, True or False: {ALL_QUESTIONS[index]["question"]}'
            self.send_all(message)
            correct_ans = ALL_QUESTIONS[index]["is_true"]
            threads = []

            for client_socket, client_address, player_name in self.clients:
                try:
                    ans_thread = threading.Thread(target=self.get_answer, args=(client_socket, player_name, correct_ans))
                    ans_thread.start()
                    self.history.add_to_history(player_name, Q_ASKED, 1)
                    threads.append(ans_thread)
                    print("Message sent to client at:", client_address)
                except Exception as e:
                    print("Failed to send message to client at:", client_address, "Error:", e)

            for thread in threads:
                thread.join()
            index += 1



    def manage_game(self):

        print(f"Server started, listening on IP address {SERVER_IP}")
        offer_message = self.construct_offer_packet()
        broadcast_ip = calc_broadcast_ip()
        # Start broadcasting offer announcements in a separate thread
        offer_thread = threading.Thread(target=self.send_offer_broadcast, args=(offer_message, broadcast_ip))
        offer_thread.start()
        self.accept_clients()
        self.send_welcome_message()
        self.start_game()
        if len(self.have_winner):
            self.announce_winner()
        else:
            self.send_all(NO_GOOD_ANSWERS)
        self.show_statistics()
        self.disconnect_all()
        self.manage_game()


    def announce_winner(self):
        winner = self.have_winner[0][0]
        self.history.add_to_history(winner, WINS, 1)
        message = f'GAME OVER!\nCongratulations to the winner: {BOLD} {winner}! {RESET}'
        self.send_all(message)


    def send_all(self, message):
        for client_socket, _, _ in self.clients:
            client_socket.sendall(message.encode('utf-8'))
        print(message)

    def disconnect_all(self):
        self.send_all(END_OF_GAME)
        for client_socket, _, _ in self.clients:
            client_socket.close()
        print('Game over, sending out offer requests...')


    def send_welcome_message(self):
        message = WELCOME_MESSAGE
        i = 1
        for _, _, player_name in self.clients:
            message += f'\nPlayer {i}: {player_name}'
        message += '\n==\n'
        self.send_all(message)


    def show_statistics(self):
        self.show_top_5()
        self.show_players_wins_stat()
        self.show_players_right_answer_stat()


    def show_top_5(self):
        top_5_message = 'Top 5 all time players: \n'
        top_5 = self.history.get_top_5()
        for name, wins in top_5:
            top_5_message += f'{name}: {wins} \n'

        self.send_all(top_5_message)

    def show_players_wins_stat(self):
        cur_players_message = 'Current players wins stats: \n'
        players_names = [t[0] for t in self.clients]
        current_player_h = self.history.get_current_players_wins_history(players_names)
        for name, games_played, wins, in current_player_h:
            win_pre = 0
            if games_played > 0:
                win_pre = wins/games_played
            cur_players_message += f'{name} - \nGames played: : {games_played} \nWins: {wins} \n Wins percentage: {win_pre}\n'

        self.send_all(cur_players_message)

    def show_players_right_answer_stat(self):
        cur_players_message = 'Current players answer stats: \n'
        players_names = [t[0] for t in self.clients]
        current_player_h = self.history.get_current_players_answer_history(players_names)
        for name, q_asked, q_answered, get_it_right in current_player_h:
            right_pre = 0
            if q_asked > 0:
                right_pre = get_it_right / q_asked
            cur_players_message += f'{name} - \nQuestion asked: : {q_asked} \nQuestion answered: {q_answered} \nRight answers: {get_it_right} \n' \
                                   f'Wrong answers: {q_answered-get_it_right} \nRight answers percentage: {right_pre} \ndidn\'t answer: {q_asked-q_answered} \n'

        self.send_all(cur_players_message)



class ServerHistory:


    def __init__(self):
        self.history = dict()  # dict of {player_name: info_dict} --> info_dict = {info_name (for ex: games played): num)
        self.history_lock = threading.Lock()
        self.top_5 = []


    def add_to_history(self, player_name, param, num_to_add):

        if param not in STATISTICS_DICT.keys():
            print('Invalid parameter! ')
            return None
        self.history_lock.acquire()
        try:
            if player_name not in self.history.keys():
                self.history[player_name] = STATISTICS_DICT

            self.history[player_name][param] += num_to_add

        finally:
            self.history_lock.release()
        if param == WINS:
            self.check_top_5(player_name, self.history[player_name][WINS])

    def check_top_5(self, player_name, player_wins):

        size = len(self.top_5)

        if size == 0:
            self.top_5.append((player_name, player_wins))

        elif player_wins <= self.top_5[-1][1]:
            return None

        else:
            for i in range(size):
                if self.top_5[i][1] < player_wins:
                    self.top_5.insert(i, (player_name, player_wins))
                    break
            if size >= 5:
                self.top_5.pop()

    def get_top_5(self):
        return self.top_5

    def get_current_players_wins_history(self, players_names):
        players_his = []
        for name in players_names:
            if name in self.history.keys():
                game_played = self.history[name][GAME_PLAYED]
                wins = self.history[name][WINS]
                players_his.append((name, game_played, wins))
        return players_his

    def get_current_players_answer_history(self, players_names):
        players_his = []
        for name in players_names:
            if name in self.history.keys():
                q_asked = self.history[name][Q_ASKED]
                q_answered = self.history[name][Q_ANSWERED]
                got_it_right = self.history[name][GOT_IT_RIGHT]
                players_his.append((name, q_asked, q_answered, got_it_right))
        return players_his


if __name__ == "__main__":
    s = Server("kibitz")
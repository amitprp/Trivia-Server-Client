import threading
import socket
import struct
import ReadJson
import Questions
import Network
import GameHistory
import ANSI
import Statistics
import time

json_handle = ReadJson.JsonHandle()
CONSTANTS = json_handle.read_json('Jsons/constants.json')
MESSAGES = json_handle.read_json('Jsons/messages.json')
HISTORY = json_handle.read_json('Jsons/history.json')


def add_to_locked_list(player, my_lock, list_to_add):
    my_lock.acquire()
    try:
        list_to_add.append(player)
    finally:
        my_lock.release()


def get_bool_ans(str_player_ans):
    if str_player_ans is None:
        return None
    lower_ans = str_player_ans.lower()
    if lower_ans in CONSTANTS['POSSIBLE_TRUE_ANSWERS']:
        return True
    elif lower_ans in CONSTANTS['POSSIBLE_FALSE_ANSWERS']:
        return False
    return None


def check_answer(answer, correct_answer):
    return answer == correct_answer


class GameServer:


    def __init__(self, name):

        self.name = name
        self.question_manager = Questions.Questions()
        self.network_manager = Network.Network()

        self.clients = []
        self.clients_lock = threading.Lock()

        self.timer = 0
        self.timer_lock = threading.Lock()

        self.have_winner = []
        self.have_winner_lock = threading.Lock()

        self.history_manager = GameHistory.GameHistory()
        self.statistics_creator = Statistics.StatisticsCreator(self.history_manager)

        self.manage_game()


    def initiate_game_ds(self):
        self.have_winner = []
        self.timer = 0
        self.clients = []

    def send_offer_broadcast(self, message, broadcast):

        while self.timer < CONSTANTS['TIME_OUT_IN_SEC']:
            self.network_manager.get_udp_socket().sendto(message, (broadcast, CONSTANTS['UDP_PORT']))
            print("Offer broadcast")
            print(message)
            self.add_to_timer()
            time.sleep(1)


    def handle_client(self, client_sock, client_add):

        print(f"Connection from {client_add}")
        player_name = client_sock.recv(1024).decode('utf-8').strip()
        print(f"Received player name: {player_name}")
        player_tup = (client_sock, client_add, player_name)
        self.history_manager.add_to_history(player_name, HISTORY['GAME_PLAYED'], 1)
        add_to_locked_list(player_tup, self.clients_lock, self.clients)

    def accept_clients(self):

        tcp_socket = self.network_manager.get_tcp_socket()
        tcp_socket.settimeout(CONSTANTS['TIME_OUT_IN_SEC'])

        # Accept client connections for the specified duration
        while True:
            try:
                client_socket, client_address = tcp_socket.accept()
                print("Accepted connection from:", client_address)
                self.reset_timer()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.start()
            except socket.timeout:
                print("Timeout reached. No more clients will be accepted.")
                break
            except BlockingIOError:
                print("No incoming connections pending")
            except socket.error as e:
                print("Socket error:", e)

        if len(self.clients) < 1:
            print('There is no enough players right now!')
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
        offer_packet = struct.pack('!IB32sH', int(CONSTANTS['MAGIC_COOKIE'], 16), int(CONSTANTS['MESSAGE_TYPE'], 16), server_name_bytes, self.network_manager.get_tcp_port())
        return offer_packet


    def get_answer(self, client_socket, player_name, correct_ans):

        client_socket.settimeout(CONSTANTS['TIME_OUT_IN_SEC'])

        try:
            player_ans = client_socket.recv(CONSTANTS['BUFFER_SIZE'])

        except socket.timeout:
            self.network_manager.send_message(client_socket, MESSAGES['NO_ANSWER'])
            player_ans = None

        except (ConnectionResetError, ConnectionAbortedError):
            print("Connection reset or aborted by the client.")
            player_ans = None
            client_socket.close()
            self.remove_client(client_socket, player_name)
        if player_ans is None:
            str_player_ans = None
        else:
            str_player_ans = player_ans.decode('utf-8')
        answer = get_bool_ans(str_player_ans)

        if check_answer(answer, correct_ans):
            player = (player_name, client_socket)
            add_to_locked_list(player, self.have_winner_lock, self.have_winner)
            self.history_manager.add_to_history(player_name, HISTORY['Q_ANSWERED'], 1)
            self.history_manager.add_to_history(player_name, HISTORY['GOT_IT_RIGHT'], 1)
            self.network_manager.send_message(client_socket, MESSAGES['RIGHT_ANSWER'])
        elif answer is None:
            self.network_manager.send_message(client_socket, MESSAGES['INVALID_ANSWER'])
        else:
            self.network_manager.send_message(client_socket, MESSAGES['WRONG_ANSWER'])
            self.history_manager.add_to_history(player_name, HISTORY['Q_ANSWERED'], 1)


    def start_game(self):

        index = 0
        self.question_manager.shuffle_questions()

        while len(self.have_winner) == 0 and index < self.question_manager.get_len():

            message = f'Question {index+1}, True or False: {self.question_manager.get_question_at_index(index)}'
            self.send_all(message)
            correct_ans = self.question_manager.get_answer_at_index(index)
            time.sleep(0.5)
            threads = []

            for client_socket, client_address, player_name in self.clients:
                try:
                    ans_thread = threading.Thread(target=self.get_answer, args=(client_socket, player_name, correct_ans))
                    ans_thread.start()
                    self.history_manager.add_to_history(player_name, HISTORY['Q_ASKED'], 1)
                    threads.append(ans_thread)
                    print("Message sent to client at:", client_address)
                except Exception as e:
                    print("Failed to send message to client at:", client_address, "Error:", e)

            for thread in threads:
                thread.join()
            index += 1


    def manage_game(self):
        self.initiate_game_ds()
        print(f"Server started, listening on IP address {self.network_manager.get_ip_address()}")
        offer_message = self.construct_offer_packet()
        broadcast_ip = self.network_manager.calc_broadcast_ip()
        # Start broadcasting offer announcements in a separate thread
        offer_thread = threading.Thread(target=self.send_offer_broadcast, args=(offer_message, broadcast_ip))
        offer_thread.start()
        self.accept_clients()
        self.send_welcome_message()
        self.start_game()
        if len(self.have_winner):
            self.announce_winner()
        else:
            self.send_all(MESSAGES['NO_GOOD_ANSWERS'])
        self.show_statistics()

        self.disconnect_all()
        self.manage_game()


    def announce_winner(self):
        winner = self.have_winner[0][0]
        self.history_manager.add_to_history(winner, HISTORY['WINS'], 1)
        message = f'GAME OVER!\nCongratulations to the winner: {ANSI.BOLD} {winner}! {ANSI.RESET}\n\n'
        self.send_all(message)


    def send_all(self, message):
        try:
            for client_socket, _, _ in self.clients:
                client_socket.sendall(message.encode('utf-8'))
                print(message)
        except ConnectionRefusedError:
            print("Connection refused: The client is not running or is unreachable")
        except TimeoutError:
            print("Connection timed out: The client did not respond within the specified timeout")
        except OSError as e:
            print(f"OS Error: {e}")


    def disconnect_all(self):
        self.send_all(MESSAGES['END_OF_GAME'])
        try:
            for client_socket, _, _ in self.clients:
                client_socket.close()
            print('Game over, sending out offer requests...')
        except socket.error as e:
            print(f"Socket error while closing: {e}")
        except ResourceWarning as e:
            print(f"Resource warning while closing: {e}")



    def send_welcome_message(self):
        message = MESSAGES['WELCOME_MESSAGE']
        i = 1
        for _, _, player_name in self.clients:
            message += f'\nPlayer {i}: {player_name}\n==\n'
        self.send_all(message)

    def show_statistics(self):
        clients_names = [c[2] for c in self.clients]
        statistics_tup = self.statistics_creator.give_statistics(clients_names)
        for stat in statistics_tup:
            self.send_all(stat)

    def remove_client(self, client_socket, player_name):
        for socket1, address, name in self.clients:
            if socket1 == client_socket and name == player_name:
                self.clients.remove((socket1, address, name))



if __name__ == "__main__":
    s = GameServer("MambaMentality")

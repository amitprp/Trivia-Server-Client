import multiprocessing

from Client.client_state import *


# TODO: add comments to the code!!!

class TriviaClient:
    def __init__(self, player_name, number_of_players):
        self.state = LookingForServerState(self)
        self.player_name = player_name
        self.server_NAME = None
        self.server_IP = None
        self.server_PORT = None
        self.server_SOCKET = None
        self.run()
        # self.start_game(number_of_players)

    def run(self):

        self.initialize_game()
        try:
            connected = False
            while not connected:
                connected, server_NAME, server_IP, server_PORT = self.state.handle()
                if server_NAME and server_IP and server_PORT:
                    self.server_NAME = server_NAME
                    self.server_IP = server_IP
                    self.server_PORT = server_PORT
                    print(server_IP)
                else:
                    print("Error occurred in connection.")
                    break
                # connect through TCP
                self.next_state()
                connected, self.server_SOCKET = self.state.handle()
                print(self.server_SOCKET)
                if not connected or self.server_SOCKET is None:
                    print("Server disconnected, listening for offer requests...")
                    break
                print("have server connection")
                # pass to game mode
                self.next_state()
                self.state.handle()
                break
        except ConnectionResetError:
            print('Problem with the socket. trying again!')
        finally:
            self.run()  # TODO: the second time dont work properly. need to be fixed


    def next_state(self):
        state_type = type(self.state)
        if state_type is LookingForServerState:
            self.state = ConnectingToServerState(self.server_IP, self.server_PORT, self.server_NAME, self.player_name)
        elif state_type is ConnectingToServerState:
            self.state = GameModeState(self.server_SOCKET)

    def initialize_game(self):
        if self.server_SOCKET is not None:
            self.server_SOCKET.close()
        self.state = LookingForServerState(self)
        self.server_NAME = None
        self.server_IP = None
        self.server_PORT = None
        self.server_SOCKET = None

    def start_game(self, number_of_players):
        processes = []
        for _ in range(number_of_players):
            process = multiprocessing.Process(target=self.run)
            process.start()
            processes.append(process)
        for process in processes:
            process.join()


if __name__ == "__main__":
    client = TriviaClient("Amit", 1)  # TODO: get different name each time we run the server (תסתכל בעבודה נראלי רשום על זה משהו)
    # TODO: check if everything work using cmd


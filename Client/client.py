import multiprocessing

from Client.client_state import *


class TriviaClient:
    def __init__(self, player_name, number_of_players):
        self.state = LookingForServerState(self)
        self.player_name = player_name
        self.server_NAME = None
        self.server_IP = None
        self.server_PORT = None
        self.server_SOCKET = None
        # self.start_game(number_of_players)

    def run(self):
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
            # connect through TCP
            self.next_state()
            connected, self.server_SOCKET = self.state.handle()
            if not connected or self.server_SOCKET is None:
                print("Server disconnected, listening for offer requests...")
                self.to_listen_state()
                continue
            print("have server connection")
            # pass to game mode
            self.next_state()
            self.state.handle()


    def next_state(self):
        state_type = type(self.state)
        if state_type is LookingForServerState:
            self.state = ConnectingToServerState(self.server_IP, self.server_PORT, self.server_NAME, self.player_name)
        elif state_type is ConnectingToServerState:
            self.state = GameModeState(self.server_SOCKET)

    def to_listen_state(self):
        self.state = LookingForServerState(self)

    def start_game(self, number_of_players):
        processes = []
        for _ in range(number_of_players):
            process = multiprocessing.Process(target=self.run)
            process.start()
            processes.append(process)
        for process in processes:
            process.join()


if __name__ == "__main__":
    client = TriviaClient("Kobi", 1)
    client.run()

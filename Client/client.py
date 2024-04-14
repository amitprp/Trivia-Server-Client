from Client.client_state import *

class TriviaClient:
    def __init__(self, player_name):
        self.state = LookingForServerState(self)
        self.player_name = player_name
        self.server_NAME = None
        self.server_IP = None
        self.server_PORT = None
        self.server_CONNECTION = None

    def run(self):
        connected = False
        while not connected:
            connected, server_NAME, server_IP, server_PORT = self.state.handle()
            if server_NAME and server_IP and server_PORT:
                self.server_NAME = server_NAME
                self.server_IP = server_IP
                self.server_PORT = server_PORT
            else:
                print("Error occurred in connection.")
            # connect through TCP
            self.next_state()
            connected, self.server_CONNECTION = self.state.handle()
            if not connected:
                print("Server disconnected, listening for offer requests...")
                self.to_listen_state()
                continue
            # pass to game mode
            self.next_state()




    def next_state(self):
        state_type = type(self.state)
        if state_type is LookingForServerState:
            self.state = ConnectingToServerState(self.server_IP, self.server_PORT, self.server_NAME, self.player_name)
        elif state_type is ConnectingToServerState:
            self.state = GameModeState(self, self.server_CONNECTION)

    def to_listen_state(self):
        self.state = LookingForServerState(self)


if __name__ == "__main__":
    client = TriviaClient("Amit")
    client.run()

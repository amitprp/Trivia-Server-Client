import random
import time

from client_state import *
import ReadJson

json_handle = ReadJson.JsonHandle('ClientJsons')
constants = json_handle.read_json('constants.json')
# Define the UDP port to listen on
Names = constants['NAMES']


class TClient:
    """
    Represents a client for a trivia game.

    Attributes:
        state: The current state of the client.
        player_name (str): The name of the player.
        server_NAME: The name of the server.
        server_IP: The IP address of the server.
        server_PORT: The port number of the server.
        server_SOCKET: The socket connection to the server.

    Methods:
        run: Runs the client.
        next_state: Transitions to the next state.
        initialize_game: Initializes the game.
        start_game: Starts the game with multiple players.
    """

    def __init__(self):
        self.state = LookingForServerState(self)
        self.player_name = self.choose_name()
        self.server_NAME = None
        self.server_IP = None
        self.server_PORT = None
        self.server_SOCKET = None

    def run(self):
        """
        Runs the client.

        This method handles the connection to the server, transitions between different states,
        and starts the game mode.
        """
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
                self.next_state()
                connected, self.server_SOCKET = self.state.handle()
                print(self.server_SOCKET)
                if not connected or self.server_SOCKET is None:
                    print("Server disconnected, listening for offer requests...")
                    break
                print("have server connection")
                self.next_state()
                self.state.handle()
                break
        except ConnectionResetError:
            print('Problem with the socket. trying again!')
        finally:
            self.server_SOCKET.close()
            time.sleep(1)

    @staticmethod
    def choose_name():
        random_name = random.choice(Names)
        return random_name

    def next_state(self):
        """
        Transitions to the next state.

        This method determines the current state of the client and transitions to the next state accordingly.
        """
        state_type = type(self.state)
        if state_type is LookingForServerState:
            self.state = ConnectingToServerState(self.server_IP, self.server_PORT, self.server_NAME, self.player_name)
        elif state_type is ConnectingToServerState:
            self.state = GameModeState(self.server_SOCKET)

    def initialize_game(self):
        """
        Initializes the game.

        This method resets the game state and closes the server socket connection if it exists.
        """
        #
        if self.server_SOCKET is not None:
            self.server_SOCKET.close()
        self.state = LookingForServerState(self)
        self.server_NAME = None
        self.server_IP = None
        self.server_PORT = None
        self.server_SOCKET = None



class TriviaClient:
    def __init__(self):
        while True:
            self.client = TClient()
            self.client.run()
            print("next")
            del self.client


if __name__ == "__main__":
    while True:
        client = TriviaClient()

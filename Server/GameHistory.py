import jsonsHandler
import threading
import copy

json_handle = jsonsHandler.JsonHandle()
HISTORY = json_handle.read_json(r'Jsons/history.json')


class GameHistory:
    """
    Represents the game history and provides methods to manage and retrieve player statistics.

    Attributes:
        history (dict): A dictionary containing the game history for each player.
        top_5 (list): A list containing the top 5 players based on their wins.
        history_lock (threading.Lock): A lock to ensure thread safety when modifying the game history.

    Methods:
        __init__(): Initializes the GameHistory object.
        add_to_history(player_name, param, num_to_add): Adds the specified value to the player's history for the given parameter.
        check_top_5(player_name, player_wins): Checks if the player should be included in the top 5 based on their wins.
        get_top_5(): Returns the top 5 players based on their wins.
        get_current_players_wins_history(players_names): Returns the game history (games played and wins) for the specified players.
        get_current_players_answer_history(players_names): Returns the answer history (questions asked, questions answered, and correct answers) for the specified players.
        upload_to_database(): Uploads the game history to the database.
        read_from_database(): Reads the game history from the database.
    """

    def __init__(self):
        """
        Initializes the GameHistory object.

        The game history is read from the database and stored in the `history` attribute.
        The top 5 players based on their wins are stored in the `top_5` attribute.
        The `history_lock` attribute is used to ensure thread safety when modifying the game history.
        """
        self.history, self.top_5 = self.read_from_database()
        self.history_lock = threading.Lock()

    def add_to_history(self, player_name, param, num_to_add):
        """
        Adds the specified value to the player's history for the given parameter.

        Args:
            player_name (str): The name of the player.
            param (str): The parameter to update in the player's history.
            num_to_add (int): The value to add to the player's history for the given parameter.

        Returns:
            None
        """
        stats_dict = HISTORY['STATISTICS_DICT']
        wins = HISTORY['WINS']

        if param not in stats_dict.keys():
            print('Invalid parameter! ')
            return None
        self.history_lock.acquire()
        try:
            if player_name not in self.history.keys():
                self.history[player_name] = copy.deepcopy(stats_dict)

            self.history[player_name][param] += num_to_add

        finally:
            self.history_lock.release()
        if param == wins:
            self.check_top_5(player_name, self.history[player_name][wins])

    def check_top_5(self, player_name, player_wins):
        """
        Checks if the player should be included in the top 5 based on their wins.

        If the player is already in the top 5, their wins are updated.
        If the player has more wins than the player in the last position of the top 5, they are inserted at the appropriate position.
        If the top 5 is already full, the player with the lowest wins is removed.

        Args:
            player_name (str): The name of the player.
            player_wins (int): The number of wins for the player.

        Returns:
            None
        """
        size = len(self.top_5)

        if size < 5:
            self.top_5.append([player_name, player_wins])
            self.top_5 = sorted(self.top_5, key=lambda x: x[1], reverse=True)
        else:
            for player_list in self.top_5:
                if player_name == player_list[0]:
                    player_list[1] = player_wins
                    return

            if player_wins <= self.top_5[-1][1]:
                return None

            else:
                for i in range(size):
                    if self.top_5[i][1] < player_wins:
                        self.top_5.insert(i, (player_name, player_wins))
                        break
                if size >= 5:
                    self.top_5.pop()

    def get_top_5(self):
        """
        Returns the top 5 players based on their wins.

        Returns:
            list: A list of tuples containing the player name and number of wins for the top 5 players.
        """
        return self.top_5

    def get_current_players_wins_history(self, players_names):
        """
        Returns the game history (games played and wins) for the specified players.

        Args:
            players_names (list): A list of player names.

        Returns:
            list: A list of tuples containing the player name, number of games played, and number of wins for each player.
        """
        game_play = HISTORY['GAME_PLAYED']
        wins_str = HISTORY['WINS']

        players_his = []
        for name in players_names:
            if name in self.history.keys():
                game_played = self.history[name][game_play]
                wins = self.history[name][wins_str]
                players_his.append((name, game_played, wins))
        return players_his

    def get_current_players_answer_history(self, players_names):
        """
        Returns the answer history (questions asked, questions answered, and correct answers) for the specified players.

        Args:
            players_names (list): A list of player names.

        Returns:
            list: A list of tuples containing the player name, number of questions asked, number of questions answered, and number of correct answers for each player.
        """
        q_ask = HISTORY['Q_ASKED']
        q_answer = HISTORY['Q_ANSWERED']
        got_it_right_str = HISTORY['GOT_IT_RIGHT']
        players_his = []
        for name in players_names:
            if name in self.history.keys():
                q_asked = self.history[name][q_ask]
                q_answered = self.history[name][q_answer]
                got_it_right = self.history[name][got_it_right_str]
                players_his.append((name, q_asked, q_answered, got_it_right))
        return players_his

    def upload_to_database(self):
        """
        Uploads the game history to the database.

        If the top 5 players list is not empty, it is added to the game history before uploading.
        """
        if len(self.top_5) > 0:
            self.history[HISTORY['TOP_FIVE']] = self.top_5
        json_handle.dict_to_json_file(self.history)

    @staticmethod
    def read_from_database():
        """
        Reads the game history from the database.

        Returns:
            tuple: A tuple containing the game history (dict) and the top 5 players list (list).
        """
        history = json_handle.read_json(r'Jsons/Past_Results.json')
        if not history:
            return dict(), []
        else:
            top_5 = history[HISTORY['TOP_FIVE']]
            history.pop(HISTORY['TOP_FIVE'])
            return history, top_5

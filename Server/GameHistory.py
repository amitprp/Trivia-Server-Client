import ReadJson
import threading
import copy

json_handle = ReadJson.JsonHandle()
HISTORY = json_handle.read_json(r'Jsons/history.json')


class GameHistory:


    def __init__(self):

        self.history = dict()  # dict of {player_name: info_dict} --> info_dict = {info_name (for ex: games played): num)
        self.history_lock = threading.Lock()
        self.top_5 = []


    def add_to_history(self, player_name, param, num_to_add):

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

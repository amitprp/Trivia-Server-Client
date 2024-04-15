import ReadJson
import threading


class GameHistory:


    def __init__(self):

        self.history = dict()  # dict of {player_name: info_dict} --> info_dict = {info_name (for ex: games played): num)
        self.history_lock = threading.Lock()
        self.top_5 = []
        self.json_handle = ReadJson.JsonHandle()
        self.json_history_dict = self.read_history_json(r'Jsons/history.json')

    def print_g(self):
        for g in self.json_history_dict.keys():
            print(self.json_history_dict[g])

    def add_to_history(self, player_name, param, num_to_add):

        stats_dict = self.json_history_dict['STATISTICS_DICT']
        wins = self.json_history_dict['WINS']

        if param not in stats_dict.keys():
            print('Invalid parameter! ')
            return None
        self.history_lock.acquire()
        try:
            if player_name not in self.history.keys():
                self.history[player_name] = stats_dict

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

        game_played = self.json_history_dict['GAME_PLAYED']
        wins = self.json_history_dict['WINS']

        players_his = []
        for name in players_names:
            if name in self.history.keys():
                game_played = self.history[name][game_played]
                wins = self.history[name][wins]
                players_his.append((name, game_played, wins))
        return players_his

    def get_current_players_answer_history(self, players_names):
        q_asked = self.json_history_dict['Q_ASKED']
        q_answered = self.json_history_dict['Q_ANSWERED']
        got_it_right = self.json_history_dict['GOT_IT_RIGHT']
        players_his = []
        for name in players_names:
            if name in self.history.keys():
                q_asked = self.history[name][q_asked]
                q_answered = self.history[name][q_answered]
                got_it_right = self.history[name][got_it_right]
                players_his.append((name, q_asked, q_answered, got_it_right))
        return players_his

    def read_history_json(self, name):

        return self.json_handle.read_json(name)



g = GameHistory()
g.print_g()

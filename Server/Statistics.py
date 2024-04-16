class StatisticsCreator:

    def __init__(self, history_manager):
        self.history_manager = history_manager

    def give_statistics(self, clients):
        top_5 = self.show_top_5()
        wins_stat = self.show_players_wins_stat(clients)
        answers_stat = self.show_players_right_answer_stat(clients)
        return top_5, wins_stat, answers_stat


    def show_top_5(self):
        top_5_message = 'Top 5 all time players: \n'
        top_5 = self.history_manager.get_top_5()
        for name, wins in top_5:
            top_5_message += f'{name}: {wins} \n'

        return top_5_message

    def show_players_wins_stat(self, clients):
        cur_players_message = 'Current players wins stats: \n'
        players_names = [t[0] for t in clients]
        current_player_h = self.history_manager.get_current_players_wins_history(players_names)
        for name, games_played, wins, in current_player_h:
            win_pre = 0
            if games_played > 0:
                win_pre = wins/games_played
            cur_players_message += f'{name} - \nGames played: : {games_played} \nWins: {wins} \n Wins percentage: {win_pre}\n'

        return cur_players_message

    def show_players_right_answer_stat(self, clients):
        cur_players_message = 'Current players answer stats: \n'
        players_names = [t[0] for t in clients]
        current_player_h = self.history_manager.get_current_players_answer_history(players_names)
        for name, q_asked, q_answered, get_it_right in current_player_h:
            right_pre = 0
            if q_asked > 0:
                right_pre = get_it_right / q_asked
            cur_players_message += f'{name} - \nQuestion asked: : {q_asked} \nQuestion answered: {q_answered} \nRight answers: {get_it_right} \n' \
                                   f'Wrong answers: {q_answered-get_it_right} \nRight answers percentage: {right_pre} \ndidn\'t answer: {q_asked-q_answered} \n'

        return cur_players_message

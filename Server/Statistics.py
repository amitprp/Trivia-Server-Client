from Server import ANSI


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
        if len(top_5) == 0:
            return ''
        for name, wins in top_5:
            top_5_message += ANSI.BOLD + ANSI.RED_TEXT + f'{name}:' + ANSI.RESET + f' {wins} \n'

        return top_5_message

    def show_players_wins_stat(self, clients):
        if len(clients) == 0:
            return ''
        cur_players_message = 'Current players wins stats: \n'
        current_player_h = self.history_manager.get_current_players_wins_history(clients)
        for name, games_played, wins, in current_player_h:
            win_pre = 0
            if games_played > 0:
                win_pre = wins / games_played
            cur_players_message += ANSI.BOLD + ANSI.RED_TEXT + f'{name} -' + ANSI.RESET + f'\n\tGames played: : {games_played} \n\tWins: {wins} \n\tWins percentage: {win_pre}\n'

        return cur_players_message

    def show_players_right_answer_stat(self, clients):
        if len(clients) == 0:
            return ''
        cur_players_message = 'Current players answer stats: \n'
        current_player_h = self.history_manager.get_current_players_answer_history(clients)
        for name, q_asked, q_answered, get_it_right in current_player_h:
            right_pre = 0
            if q_asked > 0:
                right_pre = get_it_right / q_asked
            cur_players_message += ANSI.BOLD + ANSI.RED_TEXT + f'{name} -' + ANSI.RESET + f' \n\tQuestion asked: : {q_asked} \n\tQuestion answered: {q_answered} \n\tRight answers: {get_it_right} \n\t' \
                                                                                          f'Wrong answers: {q_answered - get_it_right} \n\tRight answers percentage: {right_pre} \n\tdidn\'t answer: {q_asked - q_answered} \n'

        return cur_players_message

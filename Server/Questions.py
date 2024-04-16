import ANSI
import ReadJson

json_handle = ReadJson.JsonHandle()
RESET = ANSI.RESET

# List of trivia questions about NBA
nba_questions = [
    {
        "question": ANSI.RED_BACKGROUND + ANSI.BLACK_TEXT + "Michael Jordan won six NBA championships with the Chicago Bulls." + RESET,
        "is_true": True},
    {
        "question": ANSI.PURPLE_BACKGROUND + ANSI.YELLOW_TEXT + "The Los Angeles Lakers have won the most NBA championships in history." + RESET,
        "is_true": True},
    {
        "question": ANSI.RED_BACKGROUND + ANSI.WHITE_TEXT + "LeBron James has won the NBA Most Valuable Player (MVP) award five times." + RESET,
        "is_true": True},
    {
        "question": ANSI.BACKGROUND_BLUE + ANSI.YELLOW_TEXT + "The Golden State Warriors set the record for most wins in an NBA regular season with 73 wins." + RESET,
        "is_true": True},
    {
        "question": ANSI.PURPLE_BACKGROUND + ANSI.YELLOW_TEXT + "Kobe Bryant scored 100 points in a single NBA game." + RESET,
        "is_true": False},
    {"question": ANSI.ORANGE_BACKGROUND + ANSI.BLACK_TEXT + "The NBA was founded in 1950." + RESET,
     "is_true": False},
    {
        "question": ANSI.WHITE_BACKGROUND + ANSI.GREEN_TEXT + "Larry Bird played his entire NBA career with the Boston Celtics." + RESET,
        "is_true": True},
    {
        "question": ANSI.ORANGE_BACKGROUND + ANSI.BLACK_TEXT + "The NBA Slam Dunk Contest was first held in 1976." + RESET,
        "is_true": True},
    {
        "question": ANSI.ORANGE_BACKGROUND + ANSI.BLACK_TEXT + "The NBA three-point line was introduced in the 1980s." + RESET,
        "is_true": False},
    {
        "question": ANSI.PURPLE_BACKGROUND + ANSI.YELLOW_TEXT + "Shaquille O'Neal was known for his exceptional three-point shooting." + RESET,
        "is_true": False}
]

# List of trivia questions about surfing
surfing_questions = [
    {"question": "Kelly Slater is considered one of the greatest surfers of all time.", "is_true": True},
    {"question": "Surfing originated in Australia.", "is_true": False},
    {"question": "The biggest wave ever surfed measured over 100 feet tall.", "is_true": True},
    {"question": "A 'barrel' in surfing refers to a surfing competition.", "is_true": False},
    {"question": "Surfing made its Olympic debut at the 2020 Tokyo Olympics.", "is_true": True},
    {"question": "Hawaii is known as the birthplace of modern surfing.", "is_true": True},
    {"question": "A 'wipeout' in surfing refers to a successful ride on a wave.", "is_true": False},
    {"question": "Surfboards were originally made from aluminum.", "is_true": False},
    {
        "question": "The term 'hang ten' refers to riding a wave with all ten toes hanging over the edge of the surfboard.",
        "is_true": True},
    {"question": "Surfing was first practiced by ancient Polynesians.", "is_true": True}
]


def format_surfing_questions():
    for q in surfing_questions:
        q['question'] = ANSI.CYAN_BACKGROUND + '~~~ ' + q['question'] + ' ~~~' + RESET


# all question formatted
format_surfing_questions()
ALL_QUESTIONS = nba_questions + surfing_questions


class Questions:

    def __init__(self):
        self.all_questions = ALL_QUESTIONS

    def get_questions(self):
        return self.all_questions

    def get_len(self):
        return len(self.all_questions)

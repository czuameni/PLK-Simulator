import random

class Team:
    def __init__(self, name, overall):
        self.name = name
        self.overall = overall

        self.offense = overall + random.uniform(-3, 3)
        self.defense = overall + random.uniform(-3, 3)

        self.points = 0
        self.wins = 0
        self.losses = 0

        self.games_played = 0

        self.scored = 0
        self.conceded = 0

        self.games_history = []

        self.players = []

        self.budget = random.randint(7000, 9000)
        self.salary_used = 0

class Game:
    def __init__(self, home, away):
        self.home = home
        self.away = away

        self.home_score = 0
        self.away_score = 0
        self.quarters = []

        self.played = False
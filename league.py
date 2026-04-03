import json
from models import Team

def update_standings(game, playoff=False):
    if hasattr(game, "counted"):
        return

    game.counted = True

    home = game.home
    away = game.away

    home.games_played += 1
    away.games_played += 1

    home.scored += game.home_score
    home.conceded += game.away_score

    away.scored += game.away_score
    away.conceded += game.home_score

    if game.home_score > game.away_score:
        home.wins += 1
        home.points += 2

        away.losses += 1
        away.points += 1
    else:
        away.wins += 1
        away.points += 2

        home.losses += 1
        home.points += 1

    game_data_home = {
        "opponent": game.away.name,
        "scored": game.home_score,
        "conceded": game.away_score,
        "quarters": game.quarters,
        "home": True,
        "result": "W" if game.home_score > game.away_score else "L",
        "playoff": playoff
    }

    game_data_away = {
        "opponent": game.home.name,
        "scored": game.away_score,
        "conceded": game.home_score,
        "quarters": game.quarters,
        "home": False,
        "result": "W" if game.away_score > game.home_score else "L",
        "playoff": playoff
    }

    home.games_history.append(game_data_home)
    away.games_history.append(game_data_away)

def get_standings(teams):
    return sorted(
        teams,
        key=lambda t: (t.points, t.scored - t.conceded),
        reverse=True
    )
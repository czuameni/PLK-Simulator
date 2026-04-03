import json
from models import Team, Game
from engine import simulate_game
from league import (
    update_standings,
    get_standings,
)
from schedule import generate_schedule


def load_teams():
    with open("data/teams.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    return [Team(t["name"], t["overall"]) for t in data]


def create_season(teams):
    return generate_schedule(teams)


def play_round(round_games):
    results = []

    for home, away in round_games:
        game = Game(home, away)

        simulate_game(game)
        update_standings(game)

        results.append(game)

    return results


def play_regular_season(teams, schedule):
    all_results = []

    for round_games in schedule:
        results = play_round(round_games)
        all_results.append(results)

    return all_results


def get_table(teams):
    return get_standings(teams)


def run_postseason(teams):
    standings = get_standings(teams)

    playin_teams = standings[:10]

    playin_winners, playin_data = play_in_tournament(playin_teams)

    playoff_teams = standings[:6] + playin_winners

    champion, playoff_data = play_offs(playoff_teams)

    return champion, playin_data, playoff_data


def simulate_full_season():
    teams = load_teams()
    schedule = create_season(teams)

    print("=== REGULAR SEASON ===")

    for i, round_games in enumerate(schedule, 1):
        print(f"\nROUND {i}")

        results = play_round(round_games)

        for g in results:
            print(f"{g.home.name} {g.home_score} - {g.away_score} {g.away.name}")

    print("\n=== FINAL STANDINGS ===")

    standings = get_table(teams)

    for i, t in enumerate(standings, 1):
        print(f"{i}. {t.name} | {t.points} pts | {t.wins}-{t.losses}")

    print("\n=== POSTSEASON ===")

    champion, playin_data, playoff_data = run_postseason(teams)

    print("\n=== PLAY-IN ===")

    for matchup in playin_data["matchups"]:
        t1, t2 = matchup["teams"]

        print(f"\n{t1.name} vs {t2.name}")

        for g in matchup["games"]:
            print(g.home.name, g.home_score, "-", g.away_score, g.away.name)

        print("Winner:", matchup["winner"].name)

    print("\n=== PLAYOFF ===")

    for round_name, data in playoff_data.items():
        print(f"\n--- {round_name.upper()} ---")

        if round_name == "final":
            games = data["games"]
            for g in games:
                print(g.home.name, g.home_score, "-", g.away_score, g.away.name)
        else:
            for matchup in data:
                for g in matchup["games"]:
                    print(g.home.name, g.home_score, "-", g.away_score, g.away.name)

    print(f"\n🏆 CHAMPION: {champion.name}")

def play_series(team1, team2, wins_needed=3):
    """
    Seria BO5 (do 3 zwycięstw)
    Gospodarz zmienia się co 2 mecze:
    1-2: team1 home
    3-4: team2 home
    5: team1 home
    """

    wins1 = 0
    wins2 = 0
    games = []

    game_number = 1

    while wins1 < wins_needed and wins2 < wins_needed:

        if game_number in [1, 2, 5]:
            home = team1
            away = team2
        else:
            home = team2
            away = team1

        game = Game(home, away)
        simulate_game(game)


        if game.home == team1:
            if game.home_score > game.away_score:
                wins1 += 1
            else:
                wins2 += 1
        else:
            if game.home_score > game.away_score:
                wins2 += 1
            else:
                wins1 += 1

        games.append(game)
        game_number += 1

    winner = team1 if wins1 > wins2 else team2

    return winner, games

def play_in_tournament(teams):
    """
    Play-in:
    7 vs 10
    8 vs 9

    Zwycięzcy → seed 7 i 8
    """

    t7 = teams[6]
    t8 = teams[7]
    t9 = teams[8]
    t10 = teams[9]

    winner1, series1 = play_series(t7, t10)
    winner2, series2 = play_series(t8, t9)

    winners = [winner1, winner2]

    playin_data = {
        "matchups": [
            {
                "teams": (t7, t10),
                "games": series1,
                "winner": winner1
            },
            {
                "teams": (t8, t9),
                "games": series2,
                "winner": winner2
            }
        ]
    }

    return winners, playin_data

def play_offs(teams):
    """
    Playoff:
    1 vs 8
    2 vs 7
    3 vs 6
    4 vs 5

    Wszystko BO5
    """

    qf_pairs = [
        (teams[0], teams[7]),
        (teams[1], teams[6]),
        (teams[2], teams[5]),
        (teams[3], teams[4]),
    ]

    qf_winners = []
    qf_data = []

    for t1, t2 in qf_pairs:
        winner, games = play_series(t1, t2)
        qf_winners.append(winner)

        qf_data.append({
            "teams": (t1, t2),
            "games": games,
            "winner": winner
        })

    sf_pairs = [
        (qf_winners[0], qf_winners[3]),
        (qf_winners[1], qf_winners[2]),
    ]

    sf_winners = []
    sf_data = []

    for t1, t2 in sf_pairs:
        winner, games = play_series(t1, t2)
        sf_winners.append(winner)

        sf_data.append({
            "teams": (t1, t2),
            "games": games,
            "winner": winner
        })

    final_winner, final_games = play_series(sf_winners[0], sf_winners[1])

    final_data = {
        "teams": (sf_winners[0], sf_winners[1]),
        "games": final_games,
        "winner": final_winner
    }

    playoff_data = {
        "quarterfinals": qf_data,
        "semifinals": sf_data,
        "final": final_data
    }

    return final_winner, playoff_data


if __name__ == "__main__":
    simulate_full_season()
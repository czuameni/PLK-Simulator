import random

def get_team_strength(team):
    if not team.players:
        return team.offense, team.defense

    top_players = sorted(team.players, key=lambda p: p.overall, reverse=True)[:5]

    offense = sum(p.offense for p in top_players) / len(top_players)
    defense = sum(p.defense for p in top_players) / len(top_players)

    return offense, defense

def simulate_quarter(home, away):
    base = random.gauss(21, 4)

    home_off, home_def = get_team_strength(home)
    away_off, away_def = get_team_strength(away)

    home_attack = home_off + random.gauss(0, 2)
    away_attack = away_off + random.gauss(0, 2)

    home_def = home_def + random.gauss(0, 2)
    away_def = away_def + random.gauss(0, 2)

    home_bonus = random.uniform(0.5, 1.2)

    home_score = base + (home_attack - away_def) * 0.35 + home_bonus
    away_score = base + (away_attack - home_def) * 0.35

    return max(10, int(home_score)), max(10, int(away_score))

def simulate_game(game):
    home_total = 0
    away_total = 0

    quarters = []

    for _ in range(4):
        h, a = simulate_quarter(game.home, game.away)

        quarters.append((h, a))

        home_total += h
        away_total += a

    while home_total == away_total:
        ot_home, ot_away = simulate_quarter(game.home, game.away)
        home_total += ot_home
        away_total += ot_away
        quarters.append(("OT", ot_home, ot_away))

    game.overtime = len(quarters) > 4

    game.home_score = home_total
    game.away_score = away_total
    game.quarters = quarters
    game.played = True

    def distribute_points(team, total_points):
        players = sorted(team.players, key=lambda p: p.overall, reverse=True)[:5]

        weights = [p.overall for p in players]
        total_weight = sum(weights)

        remaining = total_points

        for i, p in enumerate(players):
            if i == len(players) - 1:
                pts = remaining
            else:
                share = weights[i] / total_weight
                pts = int(total_points * share)

                if p.role == "star":
                    pts = int(pts * 1.4)
                elif p.role == "starter":
                    pts = int(pts * 1.1)
                elif p.role == "bench":
                    pts = int(pts * 0.7)

                if p.position in ["SG", "SF"]:
                    pts = int(pts * 1.15)
                elif p.position == "PF":
                    pts = int(pts * 1.0)
                elif p.position in ["PG", "C"]:
                    pts = int(pts * 0.85)

                if i == 0:
                    pts = int(pts * 1.2)
                elif i == 1:
                    pts = int(pts * 1.1)

                pts = max(4, pts)
                remaining -= pts

            p.points += pts
            p.games_played += 1

            import random

            if p.position in ["C"]:
                reb = random.randint(7, 15)
            elif p.position in ["PF"]:
                reb = random.randint(5, 12)
            elif p.position in ["SF"]:
                reb = random.randint(3, 8)
            else:
                reb = random.randint(1, 5)

            p.rebounds += reb

            if p.position == "PG":
                ast = random.randint(5, 12)
            elif p.position in ["SG", "SF"]:
                ast = random.randint(2, 6)
            else:
                ast = random.randint(1, 4)

            p.assists += ast

    distribute_points(game.home, game.home_score)

    distribute_points(game.away, game.away_score)

    return game
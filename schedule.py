def generate_schedule(teams):
    teams = teams[:]

    if len(teams) % 2 != 0:
        teams.append(None)

    n = len(teams)
    rounds = []

    for round_num in range(n - 1):
        pairs = []

        for i in range(n // 2):
            home = teams[i]
            away = teams[n - 1 - i]

            if home is not None and away is not None:
                if round_num % 2 == 0:
                    pairs.append((home, away))
                else:
                    pairs.append((away, home))

        rounds.append(pairs)

        teams = [teams[0]] + [teams[-1]] + teams[1:-1]

    second_half = []
    for round in rounds:
        second_half.append([(away, home) for home, away in round])

    return rounds + second_half
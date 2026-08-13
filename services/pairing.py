def pair_swiss_teams(teams, previous_pair_keys):
    """Return Swiss pairings and an optional bye team.

    teams must already be sorted in standings order. previous_pair_keys should
    contain frozensets of team ids that have already played each other.
    """

    remaining = list(teams)
    pairs = []
    bye_team = None

    if len(remaining) % 2 == 1:
        # Give the bye to the lowest-ranked team that has not already had one.
        bye_index = None
        for index in range(len(remaining) - 1, -1, -1):
            if not remaining[index].bye_received:
                bye_index = index
                break
        if bye_index is None:
            bye_index = len(remaining) - 1
        bye_team = remaining.pop(bye_index)

    while len(remaining) >= 2:
        team1 = remaining.pop(0)
        opponent_index = None

        for index, candidate in enumerate(remaining):
            pair_key = frozenset((team1.id, candidate.id))
            if pair_key not in previous_pair_keys:
                opponent_index = index
                break

        # If every available opponent is a repeat, allow the least-bad repeat
        # instead of blocking the tournament.
        if opponent_index is None:
            opponent_index = 0

        team2 = remaining.pop(opponent_index)
        pairs.append((team1, team2))

    return pairs, bye_team

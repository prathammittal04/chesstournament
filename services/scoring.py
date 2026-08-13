def calculate_match(board_scores):

    """
    board_scores example

    [1,0.5,1,0,1]
    """

    team1 = sum(board_scores)

    team2 = len(board_scores) - team1

    if team1 > team2:

        mp1 = 2
        mp2 = 0

    elif team2 > team1:

        mp1 = 0
        mp2 = 2

    else:

        mp1 = 1
        mp2 = 1

    return {

        "team1_board": team1,
        "team2_board": team2,
        "team1_match": mp1,
        "team2_match": mp2

    }
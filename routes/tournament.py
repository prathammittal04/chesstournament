from flask import Blueprint, flash, redirect, render_template, request, url_for

from models import db
from models.board_result import BoardResult
from models.match import Match
from models.player import Player
from models.round import Round
from models.team import Team
from models.tournament import Tournament
from services.pairing import pair_swiss_teams
from services.scoring import calculate_match

tournament = Blueprint("tournament", __name__)


def ordered_players(team):
    return sorted(team.players, key=lambda player: player.board_number or 0)


def auto_adjust_boards(tournament_id):
    teams = Team.query.filter_by(tournament_id=tournament_id).all()
    for team in teams:
        # Sort by highest score first. Tie-breaker is the current board number.
        sorted_players = sorted(team.players, key=lambda p: (-p.score, p.board_number))
        for index, player in enumerate(sorted_players, start=1):
            player.board_number = index
    db.session.commit()


def match_points_from_scores(team1_score, team2_score):
    if team1_score > team2_score:
        return 2, 0
    if team2_score > team1_score:
        return 0, 2
    return 1, 1


def leaderboard_query(tournament_id):
    return Team.query.filter_by(tournament_id=tournament_id).order_by(
        Team.match_points.desc(),
        Team.buchholz.desc(),
        Team.board_points.desc(),
        Team.seed.asc(),
    )


def completed_matches_for_tournament(tournament_id):
    return (
        Match.query.join(Round, Match.round_id == Round.id)
        .filter(Round.tournament_id == tournament_id, Match.completed.is_(True))
        .all()
    )


def previous_pair_keys(tournament_id):
    return {
        frozenset((match.team1_id, match.team2_id))
        for match in completed_matches_for_tournament(tournament_id)
        if match.team1_id and match.team2_id
    }


def recalculate_buchholz(tournament_id):
    teams = Team.query.filter_by(tournament_id=tournament_id).all()
    team_map = {team.id: team for team in teams}

    for team in teams:
        team.buchholz = 0

    for match in completed_matches_for_tournament(tournament_id):
        team1 = team_map.get(match.team1_id)
        team2 = team_map.get(match.team2_id)
        if team1 and team2:
            team1.buchholz += team2.match_points
            team2.buchholz += team1.match_points


def round_is_complete(round_obj):
    matches = Match.query.filter_by(round_id=round_obj.id).all()
    return bool(matches) and all(match.completed for match in matches)


def get_active_round(tournament_data):
    if tournament_data.current_round <= 0:
        return None
    return Round.query.filter_by(
        tournament_id=tournament_data.id,
        round_number=tournament_data.current_round,
    ).first()


@tournament.route("/setup", methods=["GET", "POST"])
def setup():
    if request.method == "POST":
        total_members = int(request.form["members"])
        team_size = int(request.form["team_size"])
        rounds = int(request.form["rounds"])

        if team_size <= 0 or total_members < team_size:
            flash("Team size must be valid and total members must create at least one team.", "danger")
            return redirect(url_for("tournament.setup"))

        total_teams = total_members // team_size

        new_tournament = Tournament(
            name=request.form["tournament_name"],
            total_members=total_members,
            team_size=team_size,
            total_teams=total_teams,
            total_rounds=rounds,
            current_round=0,
            status="Not Started",
        )

        db.session.add(new_tournament)
        db.session.commit()

        for i in range(total_teams):
            db.session.add(
                Team(
                    tournament_id=new_tournament.id,
                    name=f"Team {i + 1}",
                    seed=i + 1,
                )
            )

        db.session.commit()
        return redirect(url_for("tournament.edit_teams", tournament_id=new_tournament.id))

    return render_template("setup.html")

@tournament.route("/teams/<int:tournament_id>", methods=["GET", "POST"])
def edit_teams(tournament_id):
    tournament_data = Tournament.query.get_or_404(tournament_id)
    teams = Team.query.filter_by(tournament_id=tournament_id).order_by(Team.seed).all()
    
    if request.method == "POST":
        for index, team in enumerate(teams, start=1):
            # Update Team Name
            team.name = request.form.get(f"team_name_{index}")
            
            # Fetch players for this team ordered by board number
            players = Player.query.filter_by(team_id=team.id).order_by(Player.board_number).all()
            
            for board in range(1, tournament_data.team_size + 1):
                new_name = request.form.get(f"player_{index}_{board}")
                if board <= len(players):
                    # Update existing player name
                    players[board-1].name = new_name
                else:
                    # Create new player if missing
                    db.session.add(
                        Player(
                            team_id=team.id,
                            name=new_name,
                            board_number=board,
                        )
                    )
        db.session.commit()
        flash("Teams and players saved.", "success")
        return redirect(url_for("tournament.dashboard", tournament_id=tournament_id))
        
    return render_template("teams.html", tournament=tournament_data, teams=teams)


# --- Add this new route at the bottom of the file ---
@tournament.route("/team/<int:team_id>/history")
def team_history(team_id):
    team = Team.query.get_or_404(team_id)
    tournament_data = Tournament.query.get_or_404(team.tournament_id)
    
    # Fetch all completed matches involving this team
    matches = Match.query.filter(
        (Match.team1_id == team.id) | (Match.team2_id == team.id),
        Match.completed == True
    ).all()
    
    # Fetch all rounds for this tournament to map round_ids to round_numbers
    rounds = {r.id: r.round_number for r in Round.query.filter_by(tournament_id=tournament_data.id).all()}
    
    history = []
    for match in matches:
        is_team1 = match.team1_id == team.id
        opponent = match.team2 if is_team1 else match.team1
        team_score = match.team1_score if is_team1 else match.team2_score
        opponent_score = match.team2_score if is_team1 else match.team1_score
        
        if team_score > opponent_score:
            result_text = f"{team.name} won"
        elif team_score < opponent_score:
            result_text = f"{opponent.name} won"
        else:
            result_text = "Match drew"
            
        # Process individual board results
        board_details = []
        for board in sorted(match.board_results, key=lambda b: b.board_number):
            if is_team1:
                t_player, o_player = board.player1_name, board.player2_name
                t_score, o_score = board.player1_score, board.player2_score
            else:
                t_player, o_player = board.player2_name, board.player1_name
                t_score, o_score = board.player2_score, board.player1_score
            
            if t_score > o_score:
                status, color = "beat", "text-success"
            elif t_score < o_score:
                status, color = "lost to", "text-danger"
            else:
                status, color = "drew with", "text-secondary"
            
            board_details.append({
                "board_number": board.board_number,
                "team_player": t_player,
                "opponent_player": o_player,
                "team_score": t_score,
                "opponent_score": o_score,
                "status": status,
                "color": color
            })
            
        history.append({
            "round_number": rounds.get(match.round_id),
            "team_score": team_score,
            "opponent": opponent,
            "opponent_score": opponent_score,
            "result_text": result_text,
            "board_details": board_details
        })
    
    # Sort the history chronologically by round number
    history.sort(key=lambda x: x["round_number"])
    
    return render_template("team_history.html", team=team, tournament=tournament_data, history=history)

@tournament.route("/dashboard/<int:tournament_id>")
def dashboard(tournament_id):
    tournament_data = Tournament.query.get_or_404(tournament_id)
    recalculate_buchholz(tournament_id)
    db.session.commit()
    teams = leaderboard_query(tournament_id).all()
    active_round = get_active_round(tournament_data)
    top_players = Player.query.join(Team).filter(Team.tournament_id == tournament_id).order_by(Player.score.desc()).all()

    return render_template(
        "dashboard.html",
        tournament=tournament_data,
        teams=teams,
        active_round=active_round,
        top_players=top_players, 
    )


@tournament.route("/start-round/<int:tournament_id>")
def start_round(tournament_id):
    tournament_data = Tournament.query.get_or_404(tournament_id)

    if tournament_data.current_round >= tournament_data.total_rounds:
        tournament_data.status = "Completed"
        db.session.commit()
        flash("All scheduled rounds are complete.", "info")
        return redirect(url_for("tournament.dashboard", tournament_id=tournament_id))

    next_round_number = tournament_data.current_round + 1

    if tournament_data.current_round > 0:
        previous_round = Round.query.filter_by(
            tournament_id=tournament_id,
            round_number=tournament_data.current_round,
        ).first_or_404()
        if not round_is_complete(previous_round):
            flash("Enter every result in the current round before starting the next round.", "warning")
            return redirect(
                url_for(
                    "tournament.round_pairings",
                    tournament_id=tournament_id,
                    round_number=tournament_data.current_round,
                )
            )

    existing_round = Round.query.filter_by(
        tournament_id=tournament_id,
        round_number=next_round_number,
    ).first()
    if existing_round:
        return redirect(
            url_for(
                "tournament.round_pairings",
                tournament_id=tournament_id,
                round_number=next_round_number,
            )
        )

    if next_round_number == 1:
        teams = Team.query.filter_by(tournament_id=tournament_id).order_by(Team.seed).all()
    else:
        if next_round_number > 2:
            auto_adjust_boards(tournament_id)
        recalculate_buchholz(tournament_id)
        teams = leaderboard_query(tournament_id).all()

    round_obj = Round(tournament_id=tournament_id, round_number=next_round_number)
    db.session.add(round_obj)
    db.session.commit()

    pairs, bye_team = pair_swiss_teams(teams, previous_pair_keys(tournament_id))

    for table_number, (team1, team2) in enumerate(pairs, start=1):
        db.session.add(
            Match(
                round_id=round_obj.id,
                table_number=table_number,
                team1_id=team1.id,
                team2_id=team2.id,
            )
        )

    if bye_team:
        bye_team.match_points += 2
        bye_team.board_points += tournament_data.team_size
        bye_team.bye_received = True
        flash(f"{bye_team.name} received a bye: +2 match points, +{tournament_data.team_size} board points.", "info")

    tournament_data.current_round = next_round_number
    tournament_data.status = "In Progress"
    db.session.commit()

    return redirect(
        url_for(
            "tournament.round_pairings",
            tournament_id=tournament_id,
            round_number=next_round_number,
        )
    )


@tournament.route("/round/<int:tournament_id>/<int:round_number>")
def round_pairings(tournament_id, round_number):
    tournament_data = Tournament.query.get_or_404(tournament_id)
    round_obj = Round.query.filter_by(
        tournament_id=tournament_id,
        round_number=round_number,
    ).first_or_404()
    matches = Match.query.filter_by(round_id=round_obj.id).order_by(Match.table_number).all()
    all_completed = bool(matches) and all(match.completed for match in matches)

    return render_template(
        "pairings.html",
        tournament=tournament_data,
        tournament_id=tournament_id,
        round=round_obj,
        round_number=round_number,
        matches=matches,
        all_completed=all_completed,
    )

@tournament.route("/round/<int:tournament_id>/<int:round_number>/edit", methods=["GET", "POST"])
def edit_pairings(tournament_id, round_number):
    tournament_data = Tournament.query.get_or_404(tournament_id)
    round_obj = Round.query.filter_by(
        tournament_id=tournament_id, 
        round_number=round_number
    ).first_or_404()
    
    matches = Match.query.filter_by(round_id=round_obj.id).order_by(Match.table_number).all()

    if request.method == "POST":
        # Update the matches with the new team selections
        for match in matches:
            team1_id = request.form.get(f"match_{match.id}_team1")
            team2_id = request.form.get(f"match_{match.id}_team2")
            if team1_id and team2_id:
                match.team1_id = int(team1_id)
                match.team2_id = int(team2_id)
        
        db.session.commit()
        flash("Matchmaking updated successfully.", "success")
        return redirect(url_for("tournament.round_pairings", tournament_id=tournament_id, round_number=round_number))

    # Gather all teams currently playing in this round so we can populate the dropdowns
    teams_in_round = []
    for match in matches:
        if match.team1 not in teams_in_round: teams_in_round.append(match.team1)
        if match.team2 not in teams_in_round: teams_in_round.append(match.team2)
    
    return render_template(
        "edit_pairings.html", 
        tournament=tournament_data, 
        round=round_obj, 
        matches=matches, 
        teams=teams_in_round
    )


@tournament.route("/match/<int:match_id>", methods=["GET", "POST"])
def enter_result(match_id):
    match = Match.query.get_or_404(match_id)
    round_obj = Round.query.get_or_404(match.round_id)
    tournament_data = Tournament.query.get_or_404(round_obj.tournament_id)
    team1_players = ordered_players(match.team1)
    team2_players = ordered_players(match.team2)

    if request.method == "POST":
        if match.completed:
            old_mp1, old_mp2 = match_points_from_scores(match.team1_score, match.team2_score)
            match.team1.board_points -= match.team1_score
            match.team2.board_points -= match.team2_score
            match.team1.match_points -= old_mp1
            match.team2.match_points -= old_mp2
            for br in match.board_results:
                p1_ref = next((p for p in match.team1.players if p.name == br.player1_name), None)
                p2_ref = next((p for p in match.team2.players if p.name == br.player2_name), None)
                if p1_ref: p1_ref.score -= br.player1_score
                if p2_ref: p2_ref.score -= br.player2_score

        BoardResult.query.filter_by(match_id=match.id).delete()
        board_scores = []

        for i, (p1, p2) in enumerate(zip(team1_players, team2_players)):
            score = float(request.form[f"board{i}"])
            board_scores.append(score)
            p1.score += score
            p2.score += (1 - score)
            
            db.session.add(
                BoardResult(
                    match_id=match.id,
                    board_number=i + 1,
                    player1_name=p1.name,
                    player2_name=p2.name,
                    player1_score=score,
                    player2_score=1 - score,
                )
            )

        result = calculate_match(board_scores)
        match.team1_score = result["team1_board"]
        match.team2_score = result["team2_board"]
        match.completed = True

        match.team1.board_points += result["team1_board"]
        match.team2.board_points += result["team2_board"]
        match.team1.match_points += result["team1_match"]
        match.team2.match_points += result["team2_match"]

        if round_is_complete(round_obj):
            round_obj.completed = True
            tournament_data.status = "Completed" if round_obj.round_number >= tournament_data.total_rounds else "In Progress"

        recalculate_buchholz(tournament_data.id)
        db.session.commit()
        flash("Result saved. You can enter the remaining matches from this round.", "success")

        return redirect(
            url_for(
                "tournament.round_pairings",
                tournament_id=tournament_data.id,
                round_number=round_obj.round_number,
            )
        )

    existing_scores = {result.board_number: result.player1_score for result in match.board_results}
    board_rows = []
    for index, (p1, p2) in enumerate(zip(team1_players, team2_players), start=1):
        board_rows.append((index, p1, p2, existing_scores.get(index)))

    return render_template("result.html", match=match, round=round_obj, board_rows=board_rows, tournament=tournament_data)


@tournament.route("/delete/<int:tournament_id>")
def delete_tournament(tournament_id):
    tournament_data = Tournament.query.get_or_404(tournament_id)
    teams = Team.query.filter_by(tournament_id=tournament_id).all()

    for team in teams:
        Player.query.filter_by(team_id=team.id).delete()

    rounds = Round.query.filter_by(tournament_id=tournament_id).all()
    for rnd in rounds:
        matches = Match.query.filter_by(round_id=rnd.id).all()
        for match in matches:
            BoardResult.query.filter_by(match_id=match.id).delete()
        Match.query.filter_by(round_id=rnd.id).delete()

    Round.query.filter_by(tournament_id=tournament_id).delete()
    Team.query.filter_by(tournament_id=tournament_id).delete()
    db.session.delete(tournament_data)
    db.session.commit()
    flash("Tournament deleted.", "info")

    return redirect(url_for("home.index"))


@tournament.route("/tournament/<int:tournament_id>")
def tournament_dashboard(tournament_id):
    tournament_data = Tournament.query.get_or_404(tournament_id)
    return redirect(url_for("tournament.dashboard", tournament_id=tournament_data.id))

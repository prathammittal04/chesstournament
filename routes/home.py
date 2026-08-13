from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.tournament import Tournament
from models.team import Team
from models.user import User

home = Blueprint("home", __name__)

@home.route("/")
def index():
    # This is now the landing page with the two buttons
    return render_template("index.html")

@home.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Check credentials
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session["user_id"] = user.id
            return redirect(url_for("home.tournaments_list"))
        
        flash("Invalid username or password", "danger")
        
    return render_template("login.html")

@home.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("home.index"))

@home.route("/tournaments")
def tournaments_list():
    # The old home page, now protected for volunteers
    if "user_id" not in session:
        flash("Please log in to access the volunteer dashboard.", "warning")
        return redirect(url_for("home.login"))
        
    tournaments = Tournament.query.order_by(Tournament.id.desc()).all()
    return render_template("home.html", tournaments=tournaments)

@home.route("/viewer")
def viewer_tournaments():
    # Show a list of all tournaments for the viewer to choose from
    tournaments = Tournament.query.order_by(Tournament.id.desc()).all()
    return render_template("viewer_tournaments.html", tournaments=tournaments)

@home.route("/viewer/<int:tournament_id>")
def viewer_leaderboard(tournament_id):
    # Get the specific tournament the viewer clicked on
    tournament = Tournament.query.get_or_404(tournament_id)
    
    # Get teams ordered exactly like the volunteer dashboard
    teams = Team.query.filter_by(tournament_id=tournament.id).order_by(
        Team.match_points.desc(),
        Team.buchholz.desc(),
        Team.board_points.desc(),
        Team.seed.asc()
    ).all()
    
    return render_template("viewer_leaderboard.html", tournament=tournament, teams=teams)
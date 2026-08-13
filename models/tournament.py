from models import db


class Tournament(db.Model):
    __tablename__ = "tournaments"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    total_members = db.Column(db.Integer, nullable=False)

    team_size = db.Column(db.Integer, nullable=False)

    total_teams = db.Column(db.Integer, nullable=False)

    total_rounds = db.Column(db.Integer, nullable=False)

    current_round = db.Column(db.Integer, default=0)

    status = db.Column(db.String(20), default="Not Started")
from models import db

class Team(db.Model):

    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)

    tournament_id = db.Column(
        db.Integer,
        db.ForeignKey("tournaments.id")
    )

    name = db.Column(db.String(100), nullable=False)

    match_points = db.Column(db.Integer, default=0)

    board_points = db.Column(db.Float, default=0)

    buchholz = db.Column(db.Float, default=0)

    seed = db.Column(db.Integer)

    bye_received = db.Column(db.Boolean, default=False)

    players = db.relationship(
        "Player",
        backref="team",
        lazy=True,
        cascade="all, delete-orphan"
    )
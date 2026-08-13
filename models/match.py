from models import db

class Match(db.Model):
    __tablename__ = "matches"

    id = db.Column(db.Integer, primary_key=True)

    round_id = db.Column(
        db.Integer,
        db.ForeignKey("rounds.id")
    )

    table_number = db.Column(db.Integer)

    team1_id = db.Column(
        db.Integer,
        db.ForeignKey("teams.id")
    )

    team2_id = db.Column(
        db.Integer,
        db.ForeignKey("teams.id")
    )

    team1_score = db.Column(db.Float, default=0)

    team2_score = db.Column(db.Float, default=0)

    completed = db.Column(db.Boolean, default=False)

    team1 = db.relationship(
        "Team",
        foreign_keys=[team1_id]
    )

    team2 = db.relationship(
        "Team",
        foreign_keys=[team2_id]
    )
    board_results = db.relationship(
    "BoardResult",
    backref="match",
    lazy=True,
    cascade="all, delete-orphan"
)

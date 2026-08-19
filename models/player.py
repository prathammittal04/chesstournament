from models import db


class Player(db.Model):
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)

    team_id = db.Column(
        db.Integer,
        db.ForeignKey("teams.id")
    )

    name = db.Column(db.String(100), nullable=False)

    board_number = db.Column(db.Integer)
    score = db.Column(db.Float, default=0.0)
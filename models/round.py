from models import db

class Round(db.Model):
    __tablename__ = "rounds"

    id = db.Column(db.Integer, primary_key=True)

    tournament_id = db.Column(
        db.Integer,
        db.ForeignKey("tournaments.id"),
        nullable=False
    )

    round_number = db.Column(db.Integer, nullable=False)

    completed = db.Column(db.Boolean, default=False)
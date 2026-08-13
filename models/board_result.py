from models import db


class BoardResult(db.Model):
    __tablename__ = "board_results"

    id = db.Column(db.Integer, primary_key=True)

    match_id = db.Column(
        db.Integer,
        db.ForeignKey("matches.id"),
        nullable=False
    )

    board_number = db.Column(db.Integer, nullable=False)

    player1_name = db.Column(db.String(100), nullable=False)

    player2_name = db.Column(db.String(100), nullable=False)

    player1_score = db.Column(db.Float, default=0)

    player2_score = db.Column(db.Float, default=0)
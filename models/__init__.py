from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .tournament import Tournament
from .team import Team
from .player import Player
from .match import Match
from .round import Round
from .board_result import BoardResult
from .user import User
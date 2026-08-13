"""One-off copy of an old SQLite tournament.db into the Postgres DATABASE_URL.

Usage:  DATABASE_URL=postgresql://... python migrate_sqlite_to_postgres.py database/tournament.db
"""
import sqlite3
import sys

from dotenv import load_dotenv

load_dotenv()

from app import app  # noqa: E402
from models import db  # noqa: E402
from models.board_result import BoardResult  # noqa: E402
from models.match import Match  # noqa: E402
from models.player import Player  # noqa: E402
from models.round import Round  # noqa: E402
from models.team import Team  # noqa: E402
from models.tournament import Tournament  # noqa: E402
from models.user import User  # noqa: E402

ORDER = [
    ("users", User),
    ("tournaments", Tournament),
    ("teams", Team),
    ("players", Player),
    ("rounds", Round),
    ("matches", Match),
    ("board_results", BoardResult),
]


def main(path):
    src = sqlite3.connect(path)
    src.row_factory = sqlite3.Row

    with app.app_context():
        db.create_all()
        for table, model in ORDER:
            try:
                rows = src.execute(f"SELECT * FROM {table}").fetchall()
            except sqlite3.OperationalError:
                print(f"- {table}: not present, skipped")
                continue
            columns = {c.name for c in model.__table__.columns}
            copied = 0
            for row in rows:
                data = {k: row[k] for k in row.keys() if k in columns}
                if db.session.get(model, data.get("id")) is None:
                    db.session.add(model(**data))
                    copied += 1
            db.session.commit()
            print(f"- {table}: {copied} row(s) copied")

        # keep Postgres sequences ahead of the imported ids
        for table, _ in ORDER:
            db.session.execute(
                db.text(
                    "SELECT setval(pg_get_serial_sequence(:t, 'id'), "
                    "COALESCE((SELECT MAX(id) FROM " + table + "), 1))"
                ),
                {"t": table},
            )
        db.session.commit()
    print("Done.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "database/tournament.db")

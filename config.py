import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _normalize(url: str) -> str:
    """Make a Supabase/Heroku style URL usable by SQLAlchemy + psycopg 3."""
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql+psycopg://") and "sslmode=" not in url:
        url += ("&" if "?" in url else "?") + "sslmode=require"
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "chess_tournament_secret_key")

    # Set DATABASE_URL to your Supabase connection string (see SUPABASE_SETUP.md).
    # Without it we fall back to a local SQLite file, which is fine for local
    # testing but gets wiped/restored on hosts with an ephemeral disk - that is
    # what made deleted tournaments reappear.
    SQLALCHEMY_DATABASE_URI = _normalize(
        os.environ.get("DATABASE_URL")
        or "sqlite:///" + os.path.join(BASE_DIR, "database", "tournament.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Supabase's pooler drops idle connections; recycle before it does.
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

import os

from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate

load_dotenv()

from config import Config, BASE_DIR
from models import db
from models.user import User

from routes.home import home
from routes.tournament import tournament

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(home)
app.register_blueprint(tournament)


def ensure_admin_user():
    if User.query.first() is None:
        db.session.add(
            User(
                username=os.environ.get("ADMIN_USERNAME", "veersachessadmin"),
                password=os.environ.get("ADMIN_PASSWORD", "AdminAccess@2026"),
            )
        )
        db.session.commit()


with app.app_context():
    if Config.SQLALCHEMY_DATABASE_URI.startswith("sqlite"):
        os.makedirs(os.path.join(BASE_DIR, "database"), exist_ok=True)
    db.create_all()
    ensure_admin_user()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

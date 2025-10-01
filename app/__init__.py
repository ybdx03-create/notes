import os
from flask import Flask

from .database import db


def create_app() -> Flask:
    app = Flask(__name__, static_folder="static", template_folder="templates")

    database_url = os.getenv("DATABASE_URL", "sqlite:///notes_dev.db")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config.update(
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    try:
        os.makedirs(app.instance_path, exist_ok=True)  # type: ignore[arg-type]
    except OSError:
        pass

    db.init_app(app)

    with app.app_context():
        from . import models  # noqa: F401
        db.create_all()

    from .routes import bp as routes_bp

    app.register_blueprint(routes_bp)

    return app

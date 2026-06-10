from flask import Flask, g

from app.db import SessionLocal
from app.routes.health import health_bp
from app.routes.orders import orders_bp


def create_app(testing: bool = False) -> Flask:
    app = Flask(__name__)
    app.config["TESTING"] = testing

    app.register_blueprint(health_bp)
    app.register_blueprint(orders_bp)

    @app.before_request
    def open_db():
        g.db = SessionLocal()

    @app.teardown_appcontext
    def close_db(exc):
        db = g.pop("db", None)
        if db is not None and not app.config.get("TESTING"):
            db.close()

    return app

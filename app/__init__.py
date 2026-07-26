from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .config import Config, SITE
from .models import db

limiter = Limiter(key_func=get_remote_address, default_limits=[])


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    limiter.init_app(app)

    from .routes.pages import bp as pages_bp
    from .routes.auth import bp as auth_bp
    from .routes.admin import bp as admin_bp
    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    @app.context_processor
    def inject_site():
        return {"site": SITE}

    with app.app_context():
        db.create_all()

    return app

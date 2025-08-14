from flask import Flask
from .config import config
from .extensions import db, bcrypt, login_manager, csrf, migrate


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Ensure there's a secret key
    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = "your-secret-key-here"  # Change this in production!

    # Initialize extensions with the app
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Import and register blueprints
    from .blueprints.auth import auth_bp
    from .blueprints.parent import parent
    from .blueprints.child import child

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(parent, url_prefix="/parent")
    app.register_blueprint(child, url_prefix="/child")

    # User loader function
    from .models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Initialize the database tables
    with app.app_context():
        db.create_all()

    return app

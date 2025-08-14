from flask import Flask
from flask_cors import CORS
from .config import config
from .extensions import db, bcrypt, login_manager, csrf, migrate


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Enable CORS for API access from React frontend
    CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

    # Ensure there's a secret key
    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = "your-secret-key-here"  # Change this in production!

    # Initialize extensions with the app
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # API routes use @CSRFProtect.exempt decorator individually

    # Import and register blueprints
    from .blueprints.auth import auth_bp
    from .blueprints.parent import parent
    from .blueprints.child import child

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(parent, url_prefix="/parent")
    app.register_blueprint(child, url_prefix="/child")

    # API routes are now integrated into the main route files

    # User loader function
    from .models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # API error handlers
    @app.errorhandler(404)
    def api_not_found(error):
        return {"success": False, "message": "Endpoint not found"}, 404

    @app.errorhandler(500)
    def api_internal_error(error):
        return {"success": False, "message": "Internal server error"}, 500

    @app.errorhandler(401)
    def api_unauthorized(error):
        return {"success": False, "message": "Authentication required"}, 401

    @app.errorhandler(403)
    def api_forbidden(error):
        return {"success": False, "message": "Access forbidden"}, 403

    # Initialize the database tables
    with app.app_context():
        db.create_all()

    return app

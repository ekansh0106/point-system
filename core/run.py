from flask import redirect, url_for
from app import create_app
from app.blueprints.auth import auth_bp

def register_blueprints(app):
    """Register all blueprints for the application"""
    app.register_blueprint(auth_bp)
    # Add other blueprints here as needed
    
def register_error_handlers(app):
    """Register error handlers for the application"""
    @app.errorhandler(404)
    def not_found_error(error):
        return "Page not found", 404
        
    @app.errorhandler(500)
    def internal_error(error):
        return "Internal server error", 500

def init_app():
    """Initialize the core application"""
    app = create_app('development')  # or 'production' in prod environment
    register_blueprints(app)
    register_error_handlers(app)
    return app

app = init_app()

@app.route("/", methods=["GET"])
def landing():
    return redirect(url_for('auth.login'))

if __name__ == "__main__":
    app.run(debug=True)
from flask import redirect, url_for
from core.app import create_app, db
from flask_migrate import Migrate

def register_error_handlers(app):
    """Register error handlers for the application"""
    @app.errorhandler(404)
    def not_found_error(error):
        return "Page not found", 404
        
    @app.errorhandler(500)
    def internal_error(error):
        return "Internal server error", 500

# Create the application instance
app = create_app()
migrate = Migrate(app, db)
# Register error handlers
register_error_handlers(app)

@app.route("/", methods=["GET"])
def landing():
    return redirect(url_for('auth.login'))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
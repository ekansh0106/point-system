from flask import Blueprint

dashboard_bp = Blueprint("dashboard", __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/dashboard/static')

# Import routes after blueprint creation to avoid circular imports
from . import routes, forms 
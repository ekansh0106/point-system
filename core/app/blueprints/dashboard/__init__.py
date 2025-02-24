from flask import Blueprint

dashboard_bp = Blueprint('dashboard', __name__, 
                        template_folder='templates',
                        url_prefix='/dashboard')


# Import routes after blueprint creation to avoid circular imports
from . import routes, forms 
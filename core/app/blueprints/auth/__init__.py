from flask import Blueprint

auth_bp = Blueprint('auth', __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/auth/static')

# Import routes after blueprint creation to avoid circular imports
from . import routes, forms

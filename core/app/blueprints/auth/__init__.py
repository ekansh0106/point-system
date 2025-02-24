from flask import Blueprint

auth_bp = Blueprint('auth', __name__, 
                   template_folder='templates',
                   url_prefix='/auth')

from . import routes, forms  # Import at the end to avoid circular imports

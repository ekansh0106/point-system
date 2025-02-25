from flask import Blueprint

parent_bp = Blueprint('parent', __name__, url_prefix='/parent')

from . import routes 
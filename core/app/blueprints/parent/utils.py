from functools import wraps
from flask import jsonify
from flask_login import current_user


def parent_required(f):
    """Decorator to check if the current user is a parent"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.role == "parent":
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "This endpoint is only accessible to parent accounts",
                    }
                ),
                403,
            )
        return f(*args, **kwargs)

    return decorated_function

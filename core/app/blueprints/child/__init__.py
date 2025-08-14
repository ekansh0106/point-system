from flask import Blueprint

# Import the blueprint instance from routes
from .routes import child

# No need to create a new blueprint instance here
__all__ = ["child"]

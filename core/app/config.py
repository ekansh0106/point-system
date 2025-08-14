import os
from datetime import timedelta


class Config:
    # Basic Flask config
    SECRET_KEY = os.environ.get("SECRET_KEY") or "supersecretkey"

    # SQLAlchemy config
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///users.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session config
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Bcrypt config
    BCRYPT_LOG_ROUNDS = 12


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    # In production, ensure to set SECRET_KEY via environment variable


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}

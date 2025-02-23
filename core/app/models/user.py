from datetime import datetime
import pytz
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), nullable=False)  # 'parent' or 'child'
    
    # For child users, reference to their parent
    parent_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # For parent users, list of their children
    children = db.relationship('User', backref=db.backref('parent', remote_side=[id]),
                             lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_parent(self):
        return self.role == 'parent'
    
    def is_child(self):
        return self.role == 'child'
    
    def __repr__(self):
        return f'<User {self.username}>'

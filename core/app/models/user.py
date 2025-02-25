import uuid
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from core.app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # New fields for parent-child relationship
    parent_code = db.Column(db.String(32), unique=True)  # For parent accounts
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # For child accounts
    
    # Relationship fields
    children = db.relationship('User', 
                             backref=db.backref('parent', remote_side=[id]),
                             foreign_keys=[parent_id])

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        if self.role == 'parent':
            self.generate_parent_code()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_parent_code(self):
        """Generate a unique parent code"""
        while True:
            code = str(uuid.uuid4())[:8].upper()  # Generate 8-character unique code
            if not User.query.filter_by(parent_code=code).first():
                self.parent_code = code
                break

    def to_dict(self):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
        }
        if self.role == 'parent':
            data['parent_code'] = self.parent_code
            data['children'] = [child.to_dict_basic() for child in self.children]
        elif self.role == 'child':
            data['parent'] = self.parent.to_dict_basic() if self.parent else None
        return data

    def to_dict_basic(self):
        """Basic representation without recursive relationships"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role
        }

    @property
    def child_count(self):
        """Return the number of children for this user"""
        return len(self.children)

    def is_parent(self):
        """Check if the user is a parent"""
        return self.role == 'parent'

    def is_child(self):
        """Check if the user is a child"""
        return self.role == 'child'
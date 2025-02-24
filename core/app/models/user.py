from flask_login import UserMixin
from core.app import db, login_manager
from datetime import datetime
import pytz
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))
    is_active = db.Column(db.Boolean, default=True)
    
    # Parent-Child relationship
    parent_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    children = db.relationship('User',
        backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic'
    )

    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def is_parent(self):
        return self.role == 'parent'
    
    def is_child(self):
        return self.role == 'child'
    
    def __repr__(self):
        return f'<User {self.username}>'

    def add_child(self, child):
        if self.role != 'parent':
            raise ValueError("Only parent users can add children")
        if child.role != 'child':
            raise ValueError("Can only add users with child role")
        child.parent_id = self.id
        db.session.commit()

    def remove_child(self, child):
        if self.role != 'parent':
            raise ValueError("Only parent users can remove children")
        if child.parent_id != self.id:
            raise ValueError("Can only remove your own children")
        child.parent_id = None
        db.session.commit()

    def get_children(self):
        if self.role != 'parent':
            return []
        return self.children.all()

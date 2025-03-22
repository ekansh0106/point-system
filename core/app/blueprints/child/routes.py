from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from core.app.models.user import User
from core.app.extensions import db
from core.app.utils.decorators import child_required

# Change the blueprint name to match the registration in __init__.py
child = Blueprint('child', __name__, template_folder='templates')

@child.route('/')
def root():
    """Root route that redirects to appropriate dashboard based on user status"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    if current_user.role == 'parent':
        flash('Access denied. This area is for children only.', 'error')
        return redirect(url_for('parent.dashboard'))
        
    return redirect(url_for('child.dashboard'))

@child.route('/dashboard')
@login_required
@child_required
def dashboard():
    return render_template('child/dashboard.html', body_class='dashboard-page')

@child.route('/profile')
@login_required
@child_required
def profile():
    return render_template('child/profile.html', body_class='profile-page') 
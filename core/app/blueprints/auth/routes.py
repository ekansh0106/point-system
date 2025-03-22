from flask import Blueprint, render_template, redirect, url_for, flash, request, session, get_flashed_messages, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from core.app.extensions import db, bcrypt
from core.app.models.user import User
from . import auth_bp
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'parent':
            return redirect(url_for('parent.dashboard'))
        else:
            return redirect(url_for('child.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        logger.debug(f"Login attempt for email: {email}")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('parent.dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html', body_class='auth-page')

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.role == 'parent':
            return redirect(url_for('parent.dashboard'))
        else:
            return redirect(url_for('child.dashboard'))

    if request.method == 'GET':
        return render_template('auth/register.html')

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        parent_code = request.form.get('parent_code')

        # Basic validation
        if not all([username, email, password, confirm_password]):
            flash('All fields are required', 'error')
            return redirect(url_for('auth.register'))

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('auth.register'))

        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return redirect(url_for('auth.register'))

        # Handle child registration
        if parent_code:
            parent = User.query.filter_by(parent_code=parent_code, role='parent').first()
            if not parent:
                flash('Invalid parent code', 'error')
                return redirect(url_for('auth.register'))

        # Create new user
        user = User(username=username, email=email, role='parent' if not parent_code else 'child')
        user.set_password(password)

        # Link child to parent if applicable
        if parent_code:
            user.parent_id = parent.id

        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration', 'error')
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html',body_class='auth-page')
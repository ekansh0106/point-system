from flask import Blueprint, render_template, redirect, url_for, flash, request, session, get_flashed_messages
from flask_login import login_user, logout_user, login_required, current_user
from core.app import db, bcrypt
from core.app.models.user import User
from . import auth_bp  # Import auth_bp from the current package
from .forms import LoginForm, RegistrationForm
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    logger.debug(f"Flash messages at login: {get_flashed_messages(with_categories=True)}")
    
    if request.method == 'GET':
        return render_template('auth/login.html')

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        logger.debug(f"Login attempt for email: {email}")

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        
        flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'GET':
        return render_template('auth/register.html')

    if request.method == 'POST':
        try:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            role = request.form.get('role')

            logger.debug(f"Registration attempt for email: {email}")

            # Validation checks
            if not all([username, email, password, confirm_password, role]):
                flash('All fields are required', 'error')
                return render_template('auth/register.html')

            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return render_template('auth/register.html')

            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'error')
                return render_template('auth/register.html')

            if User.query.filter_by(username=username).first():
                flash('Username already taken', 'error')
                return render_template('auth/register.html')

            # Create new user
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(
                username=username,
                email=email,
                password=hashed_password,
                role=role
            )

            db.session.add(new_user)
            db.session.commit()

            logger.debug("User registered successfully")
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error: {str(e)}")
            flash(f'An error occurred during registration: {str(e)}', 'error')
            return render_template('auth/register.html')

    return render_template('auth/register.html')
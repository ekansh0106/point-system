from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from core.app.models.user import User
from core.app import db, bcrypt
from . import dashboard_bp
from .forms import AddChildForm, UpdateChildForm, ParentSettingsForm

@dashboard_bp.route('/')
@login_required
def index():
    if current_user.role == 'parent':
        return redirect(url_for('dashboard.parent_dashboard'))
    else:
        return redirect(url_for('dashboard.child_dashboard'))

@dashboard_bp.route('/parent')
@login_required
def parent_dashboard():
    if not current_user.is_parent():
        flash('Access denied. Parents only.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    return render_template('dashboard/parent_dashboard.html')

@dashboard_bp.route('/child')
@login_required
def child_dashboard():
    if not current_user.is_child():
        flash('Access denied. Children only.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    return render_template('dashboard/child_dashboard.html')

@dashboard_bp.route('/parent/add_child', methods=['GET', 'POST'])
@login_required
def add_child():
    if not current_user.is_parent():
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
    
    form = AddChildForm()
    if form.validate_on_submit():
        child = User(
            username=form.username.data,
            email=form.email.data,
            role='child',
            parent=current_user
        )
        child.set_password(form.password.data)
        db.session.add(child)
        db.session.commit()
        flash('Child account created successfully!', 'success')
        return redirect(url_for('dashboard.parent_dashboard'))
    
    return render_template('dashboard/add_child.html', form=form)

@dashboard_bp.route('/parent/update_child/<int:child_id>', methods=['GET', 'POST'])
@login_required
def update_child(child_id):
    if not current_user.is_parent():
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
    
    child = User.query.get_or_404(child_id)
    if child.parent != current_user:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.parent_dashboard'))
    
    form = UpdateChildForm(child.username)
    if form.validate_on_submit():
        child.username = form.username.data
        child.email = form.email.data
        child.is_active = (form.status.data == 'active')
        db.session.commit()
        flash('Child account updated successfully!', 'success')
        return redirect(url_for('dashboard.parent_dashboard'))
    elif request.method == 'GET':
        form.username.data = child.username
        form.email.data = child.email
        form.status.data = 'active' if child.is_active else 'inactive'
    
    return render_template('dashboard/update_child.html', form=form, child=child)

@dashboard_bp.route('/parent/settings', methods=['GET'])
@login_required
def parent_settings():
    if current_user.role != 'parent':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Get child accounts for the parent
    child_accounts = User.query.filter_by(parent_id=current_user.id).all()
    
    return render_template('dashboard/parent_settings.html', child_accounts=child_accounts)

@dashboard_bp.route('/parent/settings/update', methods=['POST'])
@login_required
def update_parent_settings():
    if current_user.role != 'parent':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    username = request.form.get('username')
    email = request.form.get('email')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_new_password = request.form.get('confirm_new_password')
    
    # Validate username uniqueness (if changed)
    if username != current_user.username:
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already taken', 'danger')
            return redirect(url_for('dashboard.parent_settings'))
    
    # Validate email uniqueness (if changed)
    if email != current_user.email:
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'danger')
            return redirect(url_for('dashboard.parent_settings'))
    
    # Update basic info
    current_user.username = username
    current_user.email = email
    
    # Update password if provided
    if current_password and new_password and confirm_new_password:
        if not bcrypt.check_password_hash(current_user.password, current_password):
            flash('Current password is incorrect', 'danger')
            return redirect(url_for('dashboard.parent_settings'))
        
        if new_password != confirm_new_password:
            flash('New passwords do not match', 'danger')
            return redirect(url_for('dashboard.parent_settings'))
        
        current_user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    
    db.session.commit()
    flash('Settings updated successfully', 'success')
    return redirect(url_for('dashboard.parent_settings'))

@dashboard_bp.route('/parent/child/add', methods=['POST'])
@login_required
def add_child_account():
    if current_user.role != 'parent':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    child_username = request.form.get('child_username')
    child_email = request.form.get('child_email')
    child_password = request.form.get('child_password')
    
    # Validate username uniqueness
    existing_user = User.query.filter_by(username=child_username).first()
    if existing_user:
        flash('Username already taken', 'danger')
        return redirect(url_for('dashboard.parent_settings'))
    
    # Validate email uniqueness
    existing_user = User.query.filter_by(email=child_email).first()
    if existing_user:
        flash('Email already registered', 'danger')
        return redirect(url_for('dashboard.parent_settings'))
    
    # Create child user
    child_user = User(
        username=child_username,
        email=child_email,
        role='child',
        parent_id=current_user.id
    )
    child_user.set_password(child_password)  # Use the model's method
    
    db.session.add(child_user)
    db.session.commit()
    
    flash('Child account created successfully', 'success')
    return redirect(url_for('dashboard.parent_settings'))

@dashboard_bp.route('/parent/child/remove/<int:child_id>', methods=['POST'])
@login_required
def remove_child_account(child_id):
    if current_user.role != 'parent':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    child = User.query.get_or_404(child_id)
    
    # Ensure the parent owns this child account
    if child.parent_id != current_user.id:
        flash('Access denied. You can only remove your own child accounts.', 'danger')
        return redirect(url_for('dashboard.parent_settings'))
    
    db.session.delete(child)
    db.session.commit()
    
    flash('Child account removed successfully', 'success')
    return redirect(url_for('dashboard.parent_settings')) 
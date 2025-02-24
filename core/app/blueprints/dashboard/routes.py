from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from core.app import db
from core.app.models.user import User
from . import dashboard_bp
from .forms import AddChildForm, UpdateChildForm, ParentSettingsForm

@dashboard_bp.route('/')
@login_required
def index():
    # Redirect based on user role
    if current_user.role == 'parent':
        return redirect(url_for('dashboard.parent_dashboard'))
    elif current_user.role == 'child':
        return redirect(url_for('dashboard.child_dashboard'))
    else:
        return "Invalid role", 403

@dashboard_bp.route('/parent')
@login_required
def parent_dashboard():
    if current_user.role != 'parent':
        return "Unauthorized", 403
    children = current_user.get_children()
    return render_template('dashboard/parent_dashboard.html', children=children)

@dashboard_bp.route('/child')
@login_required
def child_dashboard():
    if current_user.role != 'child':
        return "Unauthorized", 403
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

@dashboard_bp.route('/parent/settings', methods=['GET', 'POST'])
@login_required
def parent_settings():
    if not current_user.is_parent():
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
    
    form = ParentSettingsForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('dashboard.parent_dashboard'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    return render_template('dashboard/parent_settings.html', form=form) 
from flask import jsonify, request, Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from core.app.models.user import User
from core.app.extensions import db
from core.app.utils.decorators import parent_required
import logging
import os

# Set up logging
logger = logging.getLogger(__name__)

# Get the directory where this file is located
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'templates')

parent = Blueprint('parent', __name__, template_folder='templates')

@parent.route('/')
def root():
    """Root route that redirects to appropriate dashboard based on user status"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    if current_user.role == 'child':
        flash('Access denied. This area is for parents only.', 'error')
        return redirect(url_for('child.dashboard'))
        
    return redirect(url_for('parent.dashboard'))

@parent.route('/dashboard')
@login_required
@parent_required
def dashboard():
    return render_template('parent/dashboard.html', body_class='dashboard-page')

@parent.route('/add_child', methods=['GET', 'POST'])
@login_required
@parent_required
def add_child():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('parent/add_child.html')

        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('parent/add_child.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('parent/add_child.html')

        # Create new child account
        child = User(
            username=username,
            email=email,
            role='child',
            parent_id=current_user.id
        )
        child.set_password(password)

        db.session.add(child)
        db.session.commit()

        flash('Child account created successfully', 'success')
        return redirect(url_for('parent.dashboard'))

    return render_template('parent/add_child.html', body_class='dashboard-page')

@parent.route('/remove_child/<int:child_id>', methods=['POST'])
@login_required
@parent_required
def remove_child_form(child_id):
    """Handle form-based child removal"""
    child = User.query.get_or_404(child_id)
    
    # Verify that the child belongs to the current parent
    if child.parent_id != current_user.id:
        flash('Unauthorized action', 'error')
        return redirect(url_for('parent.dashboard'))
    
    db.session.delete(child)
    db.session.commit()
    
    flash('Child account removed successfully', 'success')
    return redirect(url_for('parent.dashboard'))

@parent.route('/view_child/<int:child_id>')
@login_required
@parent_required
def view_child(child_id):
    child = User.query.get_or_404(child_id)
    
    # Verify that the child belongs to the current parent
    if child.parent_id != current_user.id:
        flash('Unauthorized action', 'error')
        return redirect(url_for('parent.dashboard'))
    
    return render_template('parent/view_child.html', child=child)

@parent.route('/children', methods=['GET'])
@login_required
@parent_required
def get_children():
    """Get all children associated with the current parent"""
    try:
        children = [child.to_dict_basic() for child in current_user.children]
        return jsonify({
            'success': True,
            'data': {
                'children': children,
                'parent_code': current_user.parent_code
            }
        })
    except Exception as e:
        logger.error(f"Error fetching children: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch children'
        }), 500

@parent.route('/code', methods=['GET'])
@login_required
@parent_required
def get_parent_code():
    """Get current parent's code"""
    return jsonify({
        'success': True,
        'data': {
            'parent_code': current_user.parent_code
        }
    })

@parent.route('/code/generate', methods=['POST'])
@login_required
@parent_required
def generate_new_parent_code():
    print("CSRF Token in Request:", request.form.get('csrf_token'))  # Debugging log
    current_user.generate_parent_code()
    db.session.commit()
    flash('Parent code generated successfully!', 'success')
    return redirect(url_for('parent.dashboard'))

@parent.route('/children/<int:child_id>', methods=['DELETE'])
@login_required
@parent_required
def remove_child_api(child_id):
    """API endpoint to remove a child from parent's account"""
    child = User.query.get(child_id)
    if not child or child.parent_id != current_user.id:
        return jsonify({
            'success': False,
            'error': 'Child not found or not associated with this parent'
        }), 404
    
    try:
        child.parent_id = None
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Child removed successfully'
        })
    except Exception as e:
        logger.error(f"Error removing child: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to remove child'
        }), 500

@parent.route('/children/<int:child_id>', methods=['GET'])
@login_required
@parent_required
def get_child_details(child_id):
    """Get detailed information about a specific child"""
    child = User.query.get(child_id)
    if not child or child.parent_id != current_user.id:
        return jsonify({
            'success': False,
            'error': 'Child not found or not associated with this parent'
        }), 404

    return jsonify({
        'success': True,
        'data': child.to_dict()
    })

@parent.route('/children/<int:child_id>/points', methods=['POST'])
@login_required
@parent_required
def update_child_points(child_id):
    """Update points for a child"""
    child = User.query.get(child_id)
    if not child or child.parent_id != current_user.id:
        return jsonify({
            'success': False,
            'error': 'Child not found or not associated with this parent'
        }), 404

    data = request.get_json()
    points = data.get('points')
    reason = data.get('reason')

    if points is None:
        return jsonify({
            'success': False,
            'error': 'Points value is required'
        }), 400

    try:
        # Assuming you have a points system implemented
        child.update_points(points, reason)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Points updated successfully',
            'data': {
                'current_points': child.points
            }
        })
    except Exception as e:
        logger.error(f"Error updating points: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to update points'
        }), 500
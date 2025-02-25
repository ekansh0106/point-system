from flask import jsonify, request
from flask_login import login_required, current_user
from core.app.models.user import User
from core.app import db
from . import parent_bp
from .utils import parent_required
import logging

# Set up logging
logger = logging.getLogger(__name__)

@parent_bp.route('/children', methods=['GET'])
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

@parent_bp.route('/code', methods=['GET'])
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

@parent_bp.route('/code/generate', methods=['POST'])
@login_required
@parent_required
def generate_new_parent_code():
    """Generate a new parent code"""
    try:
        current_user.generate_parent_code()
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'New parent code generated successfully',
            'data': {
                'parent_code': current_user.parent_code
            }
        })
    except Exception as e:
        logger.error(f"Error generating new parent code: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to generate new parent code'
        }), 500

@parent_bp.route('/children/<int:child_id>', methods=['DELETE'])
@login_required
@parent_required
def remove_child(child_id):
    """Remove a child from parent's account"""
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

@parent_bp.route('/children/<int:child_id>', methods=['GET'])
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

@parent_bp.route('/children/<int:child_id>/points', methods=['POST'])
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
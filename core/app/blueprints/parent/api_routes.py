from flask import request, jsonify
from flask_login import login_required, current_user
from core.app.extensions import db
from core.app.models.user import User
from core.app.utils.decorators import parent_required
from . import parent
import logging

logger = logging.getLogger(__name__)


@parent.route("/api/dashboard", methods=["GET"])
@login_required
@parent_required
def api_dashboard():
    """API endpoint for parent dashboard data"""
    try:
        children = User.query.filter_by(parent_id=current_user.id).all()
        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "parent": current_user.to_dict_basic(),
                        "children": [child.to_dict_basic() for child in children],
                        "parent_code": current_user.parent_code,
                    },
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Parent dashboard error: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred"}), 500


@parent.route("/api/children", methods=["GET"])
@login_required
@parent_required
def api_get_children():
    """API endpoint to get all children for current parent"""
    try:
        children = User.query.filter_by(parent_id=current_user.id).all()
        return (
            jsonify(
                {"success": True, "children": [child.to_dict() for child in children]}
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Get children error: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred"}), 500


@parent.route("/api/children/<int:child_id>", methods=["GET"])
@login_required
@parent_required
def api_get_child(child_id):
    """API endpoint to get specific child details"""
    try:
        child = User.query.get_or_404(child_id)

        # Verify that the child belongs to the current parent
        if child.parent_id != current_user.id:
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        return jsonify({"success": True, "child": child.to_dict()}), 200
    except Exception as e:
        logger.error(f"Get child error: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred"}), 500


@parent.route("/api/children/<int:child_id>", methods=["DELETE"])
@login_required
@parent_required
def api_remove_child(child_id):
    """API endpoint to remove a child account"""
    try:
        child = User.query.get_or_404(child_id)

        # Verify that the child belongs to the current parent
        if child.parent_id != current_user.id:
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        db.session.delete(child)
        db.session.commit()

        return (
            jsonify({"success": True, "message": "Child account removed successfully"}),
            200,
        )
    except Exception as e:
        db.session.rollback()
        logger.error(f"Remove child error: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred"}), 500


@parent.route("/api/profile", methods=["GET"])
@login_required
@parent_required
def api_get_profile():
    """API endpoint to get parent profile"""
    try:
        return jsonify({"success": True, "profile": current_user.to_dict()}), 200
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred"}), 500


@parent.route("/api/profile", methods=["PUT"])
@login_required
@parent_required
def api_update_profile():
    """API endpoint to update parent profile"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400

        # Update allowed fields
        if "username" in data:
            # Check if username is already taken by another user
            existing_user = User.query.filter_by(username=data["username"]).first()
            if existing_user and existing_user.id != current_user.id:
                return (
                    jsonify({"success": False, "message": "Username already taken"}),
                    409,
                )
            current_user.username = data["username"]

        if "email" in data:
            # Check if email is already taken by another user
            existing_user = User.query.filter_by(email=data["email"]).first()
            if existing_user and existing_user.id != current_user.id:
                return (
                    jsonify({"success": False, "message": "Email already taken"}),
                    409,
                )
            current_user.email = data["email"]

        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Profile updated successfully",
                    "profile": current_user.to_dict(),
                }
            ),
            200,
        )
    except Exception as e:
        db.session.rollback()
        logger.error(f"Update profile error: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred"}), 500

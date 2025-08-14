from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from core.app.models.user import User
from core.app.extensions import db
from core.app.utils.decorators import child_required
import logging

logger = logging.getLogger(__name__)

# Change the blueprint name to match the registration in __init__.py
child = Blueprint("child", __name__, template_folder="templates")


@child.route("/")
def root():
    """Root route that redirects to appropriate dashboard based on user status"""
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))

    if current_user.role == "parent":
        flash("Access denied. This area is for children only.", "error")
        return redirect(url_for("parent.dashboard"))

    return redirect(url_for("child.dashboard"))


@child.route("/dashboard")
@login_required
@child_required
def dashboard():
    return render_template("child/dashboard.html", body_class="dashboard-page")


@child.route("/profile")
@login_required
@child_required
def profile():
    return render_template("child/profile.html", body_class="profile-page")


# =============================================================================
# API ROUTES - JSON endpoints for React frontend
# =============================================================================


@child.route("/api/dashboard", methods=["GET"])
@login_required
@child_required
def api_dashboard():
    """API endpoint for child dashboard data"""
    try:
        parent = (
            User.query.get(current_user.parent_id) if current_user.parent_id else None
        )
        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "child": current_user.to_dict_basic(),
                        "parent": parent.to_dict_basic() if parent else None,
                        "points_balance": 0,  # TODO: Implement points system
                        "completed_tasks": 0,  # TODO: Implement tasks system
                        "available_rewards": [],  # TODO: Implement rewards system
                    },
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Child dashboard error: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred"}), 500


@child.route("/api/profile", methods=["GET"])
@login_required
@child_required
def api_get_profile():
    """API endpoint to get child profile"""
    try:
        parent = (
            User.query.get(current_user.parent_id) if current_user.parent_id else None
        )
        profile_data = current_user.to_dict()
        if parent:
            profile_data["parent"] = parent.to_dict_basic()

        return jsonify({"success": True, "profile": profile_data}), 200
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred"}), 500


@child.route("/api/profile", methods=["PUT"])
@login_required
@child_required
def api_update_profile():
    """API endpoint to update child profile"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400

        # Update allowed fields (limited for children)
        if "username" in data:
            # Check if username is already taken by another user
            existing_user = User.query.filter_by(username=data["username"]).first()
            if existing_user and existing_user.id != current_user.id:
                return (
                    jsonify({"success": False, "message": "Username already taken"}),
                    409,
                )
            current_user.username = data["username"]

        # Email updates might require parent approval in a real system
        # For now, we'll allow it but you might want to add restrictions
        if "email" in data:
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


@child.route("/api/parent", methods=["GET"])
@login_required
@child_required
def api_get_parent():
    """API endpoint to get parent information"""
    try:
        if not current_user.parent_id:
            return jsonify({"success": False, "message": "No parent associated"}), 404

        parent = User.query.get(current_user.parent_id)
        if not parent:
            return jsonify({"success": False, "message": "Parent not found"}), 404

        return jsonify({"success": True, "parent": parent.to_dict_basic()}), 200
    except Exception as e:
        logger.error(f"Get parent error: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred"}), 500

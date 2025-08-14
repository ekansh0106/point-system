from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    jsonify,
)
from flask_login import login_user, logout_user, login_required, current_user
from core.app.extensions import db, csrf
from core.app.models.user import User
from . import auth_bp
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.role == "parent":
            return redirect(url_for("parent.dashboard"))
        else:
            return redirect(url_for("child.dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        logger.debug(f"Login attempt for email: {email}")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page if next_page else url_for("parent.dashboard"))
        else:
            flash("Invalid email or password", "error")

    return render_template("auth/login.html", body_class="auth-page")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    from .forms import RegistrationForm

    if current_user.is_authenticated:
        if current_user.role == "parent":
            return redirect(url_for("parent.dashboard"))
        else:
            return redirect(url_for("child.dashboard"))

    form = RegistrationForm()

    if form.validate_on_submit():
        # Get data from form
        username = form.username.data
        email = form.email.data
        password = form.password.data
        role = form.role.data
        parent_code = form.parent_code.data

        # Handle child registration - find parent
        parent = None
        if role == "child":
            parent = User.query.filter_by(
                parent_code=parent_code, role="parent"
            ).first()
            # This should not happen due to form validation, but double-check
            if not parent:
                flash("Invalid parent code", "error")
                return render_template(
                    "auth/register.html", form=form, body_class="auth-page"
                )

        # Create new user with explicit role
        user = User(username=username, email=email, role=role)
        user.set_password(password)

        # Link child to parent if applicable
        if role == "child" and parent:
            user.parent_id = parent.id

        try:
            db.session.add(user)
            db.session.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred during registration", "error")
            logger.error(f"Registration error: {str(e)}")
            return render_template(
                "auth/register.html", form=form, body_class="auth-page"
            )

    return render_template("auth/register.html", form=form, body_class="auth-page")


# =============================================================================
# API ROUTES - JSON endpoints for React frontend
# =============================================================================


@auth_bp.route("/api/login", methods=["POST"])
@csrf.exempt
def api_login():
    """API endpoint for user login"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return (
                jsonify(
                    {"success": False, "message": "Email and password are required"}
                ),
                400,
            )

        logger.debug(f"API Login attempt for email: {email}")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return (
                jsonify(
                    {
                        "success": True,
                        "message": "Login successful",
                        "user": user.to_dict_basic(),
                        "redirect": f"/{user.role}/dashboard",
                    }
                ),
                200,
            )
        else:
            return (
                jsonify({"success": False, "message": "Invalid email or password"}),
                401,
            )

    except Exception as e:
        logger.error(f"API Login error: {str(e)}")
        return (
            jsonify({"success": False, "message": "An error occurred during login"}),
            500,
        )


@auth_bp.route("/api/logout", methods=["POST"])
@login_required
@csrf.exempt
def api_logout():
    """API endpoint for user logout"""
    try:
        logout_user()
        return jsonify({"success": True, "message": "Logged out successfully"}), 200
    except Exception as e:
        logger.error(f"API Logout error: {str(e)}")
        return (
            jsonify({"success": False, "message": "An error occurred during logout"}),
            500,
        )


@auth_bp.route("/api/register", methods=["POST"])
@csrf.exempt
def api_register():
    """API endpoint for user registration"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400

        # Extract and validate required fields
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role")
        parent_code = data.get("parent_code")

        # Basic validation
        if not all([username, email, password, role]):
            return (
                jsonify({"success": False, "message": "All fields are required"}),
                400,
            )

        if role not in ["parent", "child"]:
            return jsonify({"success": False, "message": "Invalid role"}), 400

        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            return (
                jsonify({"success": False, "message": "Username already exists"}),
                409,
            )

        if User.query.filter_by(email=email).first():
            return (
                jsonify({"success": False, "message": "Email already registered"}),
                409,
            )

        # Handle child registration - parent code validation
        parent = None
        if role == "child":
            if not parent_code:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Parent code is required for child registration",
                        }
                    ),
                    400,
                )

            parent = User.query.filter_by(
                parent_code=parent_code, role="parent"
            ).first()
            if not parent:
                return (
                    jsonify({"success": False, "message": "Invalid parent code"}),
                    400,
                )

        # Create new user
        user = User(username=username, email=email, role=role)
        user.set_password(password)

        # Link child to parent if applicable
        if role == "child" and parent:
            user.parent_id = parent.id

        db.session.add(user)
        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Registration successful",
                    "user": user.to_dict_basic(),
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"API Registration error: {str(e)}")
        return (
            jsonify(
                {"success": False, "message": "An error occurred during registration"}
            ),
            500,
        )


@auth_bp.route("/api/me", methods=["GET"])
@login_required
def api_current_user():
    """API endpoint to get current user info"""
    try:
        return jsonify({"success": True, "user": current_user.to_dict()}), 200
    except Exception as e:
        logger.error(f"API Current user error: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred"}), 500


@auth_bp.route("/api/parent-code/<parent_code>", methods=["GET"])
def api_validate_parent_code(parent_code):
    """API endpoint to validate parent code"""
    try:
        parent = User.query.filter_by(parent_code=parent_code, role="parent").first()
        if parent:
            return (
                jsonify(
                    {
                        "success": True,
                        "valid": True,
                        "parent": {"username": parent.username, "id": parent.id},
                    }
                ),
                200,
            )
        else:
            return (
                jsonify(
                    {"success": True, "valid": False, "message": "Invalid parent code"}
                ),
                200,
            )
    except Exception as e:
        logger.error(f"API Parent code validation error: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred"}), 500

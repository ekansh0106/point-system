from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    SelectField,
    EmailField,
)
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from core.app.models.user import User


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(
                min=3, max=64, message="Username must be between 3 and 64 characters"
            ),
        ],
    )
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=6, message="Password must be at least 6 characters long"),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match"),
        ],
    )
    role = SelectField(
        "Role",
        choices=[("parent", "Parent"), ("child", "Child")],
        validators=[DataRequired()],
    )
    parent_code = StringField(
        "Parent Code", validators=[Length(max=32)]
    )  # Only required for child registration
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username already taken.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email already registered.")

    def validate_parent_code(self, parent_code):
        if self.role.data == "child" and not parent_code.data:
            raise ValidationError("Parent code is required for child registration")
        if self.role.data == "child" and parent_code.data:
            # Look for parent by parent_code field, not username
            parent = User.query.filter_by(
                parent_code=parent_code.data, role="parent"
            ).first()
            if not parent:
                raise ValidationError("Invalid parent code")

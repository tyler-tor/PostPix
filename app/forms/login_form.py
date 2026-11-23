from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, ValidationError
from .filters import strip_whitespace
from sqlalchemy import select
from app.models import User, db


def user_exists(form, field):
    # Checking if user exists
    email = field.data
    user = db.session.scalar(select(User).where(User.email == email))
    if not user:
        raise ValidationError('Email provided not found.')


def password_matches(form, field):
    # Checking if password matches
    password = field.data
    email = form.data['email']
    user = db.session.scalar(select(User).where(User.email == email))
    if not user:
        raise ValidationError('No such user exists.')
    if not user.check_password(password):
        raise ValidationError('Password was incorrect.')


class LoginForm(FlaskForm):
    email = StringField('email', filters=[strip_whitespace], validators=[DataRequired(), user_exists])
    password = PasswordField('password', validators=[
                           DataRequired(), password_matches])

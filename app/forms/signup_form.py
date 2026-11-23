from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length, ValidationError
from .filters import strip_whitespace
from sqlalchemy import select
from app.models import User, db


def user_exists(form, field):
    # Checking if user exists
    email = field.data
    user = db.session.scalar(select(User).where(User.email == email))
    if user:
        raise ValidationError('Email address is already in use.')


def username_exists(form, field):
    # Checking if username is already in use
    username = field.data
    user = db.session.scalar(select(User).where(User.username == username))
    if user:
        raise ValidationError('Username is already in use.')


class SignUpForm(FlaskForm):
    # Length limits match the database columns (users.username String(40), others 255).
    username = StringField(
        'username', filters=[strip_whitespace], validators=[
            DataRequired(), Length(max=40), username_exists])
    email = StringField('email', filters=[strip_whitespace], validators=[
        DataRequired(), Length(max=255), Email(message='please input valid email'), user_exists])
    password = PasswordField('password', validators=[DataRequired(), Length(min=8, max=128)])
    first_name = StringField('first name', filters=[strip_whitespace], validators=[DataRequired(), Length(max=255)])
    last_name = StringField('last name', filters=[strip_whitespace], validators=[DataRequired(), Length(max=255)])

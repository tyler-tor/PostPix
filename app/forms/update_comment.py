from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length
from .filters import strip_whitespace


class UpdateComment(FlaskForm):
    # max matches comments.body String(255)
    body = StringField('Body', filters=[strip_whitespace], validators=[DataRequired(), Length(max=255)])

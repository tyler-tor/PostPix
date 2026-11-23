from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length
from .filters import strip_whitespace


class UpdatePost(FlaskForm):
    # max matches posts.caption String(150)
    caption = StringField('Caption', filters=[strip_whitespace], validators=[DataRequired(), Length(max=150)])

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length
from .filters import strip_whitespace


class CreatePost(FlaskForm):
    # max values match posts.img_url String(255) and posts.caption String(150)
    img_url = StringField('Image', filters=[strip_whitespace], validators=[DataRequired(), Length(max=255)])
    caption = StringField('Caption', filters=[strip_whitespace], validators=[DataRequired(), Length(max=150)])

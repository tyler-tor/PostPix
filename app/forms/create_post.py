from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from .filters import strip_whitespace


class CreatePost(FlaskForm):
    # max values match posts.img_url String(255) and posts.caption String(150)
    img_url = StringField('Image', filters=[strip_whitespace], validators=[DataRequired(), Length(max=255)])
    thumb_url = StringField('Thumbnail', filters=[strip_whitespace], validators=[Optional(), Length(max=255)])
    img_width = IntegerField('Width', validators=[Optional(), NumberRange(min=1, max=20000)])
    img_height = IntegerField('Height', validators=[Optional(), NumberRange(min=1, max=20000)])
    caption = StringField('Caption', filters=[strip_whitespace], validators=[DataRequired(), Length(max=150)])

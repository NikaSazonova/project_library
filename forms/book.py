from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class BookForm(FlaskForm):
    author = StringField('Автор', validators=[DataRequired()])
    pic_url = StringField('Ссылка на обложку', validators=[DataRequired()])
    title = StringField('Название', validators=[DataRequired()])
    content = TextAreaField("Аннотация", validators=[DataRequired()])
    file = FileField('Файл книги', validators=[DataRequired()])
    submit = SubmitField('Добавить')
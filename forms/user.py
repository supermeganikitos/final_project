from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    name = StringField('Имя пользователя', validators=[DataRequired()])
    guessed = StringField('Угаданные', validators=[DataRequired()])
    asked = StringField('Спрошенные', validators=[DataRequired()])
    submit = SubmitField('Войти')
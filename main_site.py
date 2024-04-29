from flask import Flask, url_for, request, render_template, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask import make_response


class LoginForm(FlaskForm):
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    education = StringField('Образование', validators=[DataRequired()])
    profession = StringField('Профессия', validators=[DataRequired()])
    sex = StringField('Пол', validators=[DataRequired()])
    motivation = StringField('Мотивация', validators=[DataRequired()])
    ready = StringField('Готовы?', validators=[DataRequired()])
    submit = SubmitField('Отправить')


class LoginForm1(FlaskForm):
    gender = StringField('Пол', validators=[DataRequired()])
    age = StringField('Возраст', validators=[DataRequired()])
    submit = SubmitField('Отправить')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

settings = {"user_name": input()}
if len(settings["user_name"]) != 0:
    user_name = settings["user_name"]
else:
    user_name = 'Аноним'


@app.route('/')
@app.route('/index')
def index():
    if len(settings["user_name"]) != 0:
        user_name = settings["user_name"]
    else:
        user_name = 'Аноним'
    return render_template("index.html",
                           css_url=f"{url_for('static', filename='css/style.css')}",
                           title="Главная страница", title1='Миссия Колонизация Марса',
                           title2='И на Марсе будут яблони цвести!', user_name=user_name)


@app.errorhandler(404)
def not_found(error):
    return make_response((f"Нет такой страницы, {user_name} "), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response((f"Нет такой страницы, {user_name} "), 400)


@app.route('/test_carousel', methods=['POST', 'GET'])
def return_carousel():
    if 'pics' not in settings:
        settings['pics'] = [(f"{url_for('static', filename='img/1.jpeg')}", "first"),
                            (f"{url_for('static', filename='img/2.jpeg')}", "second"),
                            (f"{url_for('static', filename='img/3.jpeg')}", "third")
                            ]
    if request.method == 'POST':
        f = request.files['file']
        settings["avatar_file"] = f.filename
        f.save(f'static/img/{f.filename}')
        settings['pics'].append((f"{url_for('static', filename=f'img/{f.filename}')}", "first"))
    return render_template('test_carousel.html', title1='Миссия Колонизация Марса',
                           title2='И на Марсе будут яблони цвести!', title='Карусель', pics=settings['pics'])


@app.route('/table', methods=['GET', 'POST'])
def table():
    form = LoginForm1()
    if form.validate_on_submit():
        gender = request.form['gender']
        age = int(request.form['age'])
        return render_template('1.html', title='По каютам!',
                               title1='Миссия Колонизация Марса', title2='И на Марсе будут яблони цвести!',
                               gender=gender, age=age)
    return render_template('3.html', title='Авторизация', title1='Миссия Колонизация Марса',
                           title2='И на Марсе будут яблони цвести!', form=form)


@app.route('/auto_answer', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    d = {}
    if form.validate_on_submit():
        d = {"Фамилия": request.form['surname'], "Имя": request.form['name'], "Образование": request.form['education'],
             "Профессия": request.form['profession'], "Пол": request.form['sex'],
             "Мотивация": request.form['motivation'],
             "Готовы?": request.form['ready']}
        return render_template('2.html', title='Добро пожаловать', title1='Миссия Колонизация Марса',
                               title2='И на Марсе будут яблони цвести!', d=d)
    return render_template('auto_answer.html', title='Авторизация', title1='Миссия Колонизация Марса',
                           title2='И на Марсе будут яблони цвести!', form=form)


def main():
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
# http://127.0.0.1:8080/

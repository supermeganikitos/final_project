from flask import Flask, url_for, request, render_template, redirect
from flask import Flask, render_template
from data import db_session
from data.users import User
from flask import make_response


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
a = 0
settings = {"user_name": input()}
if len(settings["user_name"]) != 0:
    user_name = settings["user_name"]
else:
    user_name = 'Пользователь'



@app.errorhandler(404)
def not_found(error):
    return make_response((f"Нет такой страницы, {user_name} "), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response((f"Нет такой страницы, {user_name} "), 400)


@app.route('/test_carousel', methods=['POST', 'GET'])
def return_carousel():
    if 'pics' not in settings:
        settings['pics'] = [(f"{url_for('static', filename='img/1.png')}", "first"),
                            (f"{url_for('static', filename='img/2.png')}", "second"),
                            (f"{url_for('static', filename='img/3.png')}", "third")
                            ]
    return render_template('test_carousel.html', title1='Карусель',
                           title2=f'Добро пожаловать, {user_name}!', title='Геобот', pics=settings['pics'])

@app.route("/")
def index():
    db_sess = db_session.create_session()
    users = db_sess.query(User)
    return render_template("index.html", title1='Информация',
                           title2=f'Добро пожаловать, {user_name}!', title='Геобот', news=users)

def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()
# http://127.0.0.1:8080/test_carousel

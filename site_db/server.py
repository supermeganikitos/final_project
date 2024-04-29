from flask import Flask, render_template
from data import db_session
from data.users import User


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
a = 0


def main():
    db_session.global_init("db/blogs.db")
    app.run()


@app.route("/")
def index():
    db_sess = db_session.create_session()

    users = db_sess.query(User)
    return render_template("index.html", news=users)


if __name__ == '__main__':
    main()

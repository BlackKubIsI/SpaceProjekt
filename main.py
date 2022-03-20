from flask import Flask, redirect, render_template, request
from flask_wtf import FlaskForm
from flask_login import current_user, LoginManager, login_required, logout_user, login_user
from wtforms.validators import DataRequired
from wtforms import StringField, BooleanField, SubmitField, IntegerField, DateField, PasswordField, EmailField, TextAreaField

import nasapy
import sys
import datetime 
from data.user import User
from data.post import Post
from data.like_of_post import LikeOfPost
from data.like_of_comment import LikeOfComment
from data.comment import Comment
from data import db_session

app = Flask(__name__)
app.config["SECRET_KEY"] = "random_key"

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


class NasaInterfese:
    nasa = nasapy.Nasa()

    def get_mars_img(self):
        data = self.nasa.mars_rover(earth_date="2022-03-17")
        d = {}
        for i in data:
            if i["camera"]["id"] not in list(d.keys()):
                d[i["camera"]["id"]] = {"name": i["camera"]["full_name"], "img": [i["img_src"]]}
            else:
                d[i["camera"]["id"]]["img"].append(i["img_src"])
        return d


class RegistrationForm(FlaskForm):
    nick = StringField("Nick", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('PasswordAgain', validators=[DataRequired()])
    about = TextAreaField("About", validators=[DataRequired()])
    birthday = DateField("Birthday", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    submit = SubmitField("Registration")

class LoginForm(FlaskForm):
    nick = StringField("Nick", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField("Log in")

@app.route("/")
def main():
    return render_template("base.html", title="Main")

@app.route("/pictures_of_the_day")
def pictures_of_the_day():
    return "pictures_of_the_day"

@app.route("/img_of_mars")
def images_of_mars():
    nasa_interfese = NasaInterfese()
    d = nasa_interfese.get_mars_img()
    return render_template("img_of_mars.html", cam=list(d.keys()), title="ImagesOfMars", d=d, len=len)

@app.route("/missions")
def missions():
    return "missions"

@app.route("/exoplanets")
def exoplanets():
    return "exoplanets"

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.nick == form.nick.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Incorrect login or password",
                               form=form)
    return render_template('login.html', title='Log in', form=form)

@app.route("/registration", methods=["GET", "POST"])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('registration.html', title='Registration',
                                   form=form,
                                   message="Passwords don't match")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.nick == form.nick.data).first():
            return render_template('registration.html', title='Registration',
                                   form=form,
                                   message="There is already such a user")
        user = User(
            nick=form.nick.data,
            about=form.about.data,
            address=form.address.data,
            birthday=form.birthday.data
        )
        user.set_password(form.password.data)
        login_user(user, remember=False)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('registration.html', title='Registration', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

if __name__ == "__main__":
    db_session.global_init("db/blogs.db")
    session = db_session.create_session()
    app.run(port=8080, host="127.0.0.1", debug=True)
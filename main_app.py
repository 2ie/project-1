import os
import dotenv
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
import flask_login

app = Flask(__name__)

dotenv.load_dotenv(dotenv.find_dotenv())

app.secret_key = os.getenv("FLASK_SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
db = SQLAlchemy(app)

class Person(flask_login.UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)

with app.app_context():
    db.create_all()

login_manager = flask_login.LoginManager()
login_manager.login_view = "registration"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    # querying by primary key
    return Person.query.get(int(id))

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def registration():
    error_msg = None
    if request.method == "POST":
        # begin registration process
        form_username = request.form.get("uname")
        form_password = request.form.get("password")
        form_conf_password = request.form.get("conf-password")

        # user_query will contain an object if that user exists
        user_query = Person.query.filter_by(username=form_username).first()

        if user_query:
            error_msg = "Error: A user with that username already exists!"
            return render_template("registration.html", error=error_msg)
        else:
            # user_query does not exist, validate input fields

            # if username is empty
            if form_username == "":
                error_msg = "Error: Please enter a valid username."
                return render_template("registration.html", error=error_msg)
            
            # if password is empty
            if form_password == "":
                error_msg = "Error: Please enter a valid password."
                return render_template("registration.html", error=error_msg) 
            
            # check if username contains invalid characters
            special_characters = '"!@#$%^&*()-+?_=,<>/"\''
            special_characters_username = '"!@#$%^&*()-+?=,<>/ "\''
            special_characters_password = '"!^*()-+?=,<>/ "\''
            if any(char in special_characters_username for char in form_username):
                error_msg = "Error: Username contains invalid characters, please only use alphanumeric characters and _."
                return render_template("registration.html", error=error_msg)
            else:
                # username has been validated, check that passwords match
                if form_password == form_conf_password:
                    # passwords match, correct characters?
                    if any(char in special_characters_password for char in form_password):
                        error_msg = "Error: Password contains invalid characters, please only use alphanumeric characters, @, #, $, %, and _."
                        return render_template("registration.html", error=error_msg)
                    else:
                        # passwords follow conventions, add user to database
                        enc_password = sha256_crypt.encrypt(form_password)
                        new_account = Person(username=form_username, password=enc_password)
                        db.session.add(new_account)
                        db.session.commit()

                        succ_msg = "User was successfully created!"
                        return render_template("registration.html", succ=succ_msg)
                        
                else:
                    error_msg = "Error: Passwords do not match."
                    return render_template("registration.html", error=error_msg)
    else:
        return render_template("registration.html", error=error_msg)

@app.route("/login", methods=["GET", "POST"])
def login():
    error_msg = None
    if request.method == "POST":
        # begin login process
        form_username = request.form.get("uname")
        form_password = request.form.get("password")

        # if username is empty
        if form_username == "":
            error_msg = "Error: Please enter a valid username."
            return render_template("login.html", error=error_msg)
        
        if form_password == "":
            error_msg = "Error: Please enter a valid password."
            return render_template("login.html", error=error_msg)

        # user_query will contain an object if that user exists
        user_query = Person.query.filter_by(username=form_username).first()
        if user_query:
            # that user exists, check if inputted password matches database encrypted password
            enc_password_obj = (db.session.query(Person.password).filter_by(username=form_username).all())
            enc_password_obj = [row for row, in enc_password_obj]
            enc_password = enc_password_obj[0]

            # sha256_crypt.verify returns true or false depending on if user inputted password matches encrypted password
            if sha256_crypt.verify(form_password, enc_password):
                flask_login.login_user(user_query)
                return redirect(url_for("index"))
            else:
                # password could not be verified
                error_msg = "Error: Password is incorrect."
                return render_template("login.html", error=error_msg)
        else:
            # username was not found in database
            error_msg = "Error: No user with that username could be found."
            return render_template("login.html", error=error_msg)
    else:
        return render_template("login.html", error=error_msg)
    
@app.route("/index", methods=["GET", "POST"])
def index():
    return "Hello world!"

app.run(debug=True)

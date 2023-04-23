import os
import dotenv
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
from datetime import datetime 
import flask_login
#from flask_login import login_required
import requests

from zipcode_to_location import zipcode_to_location
from serp_req import get_showtime_data

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

# To fix initial 404 NOT FOUND when first navigating to website.
# Old workaround == have user add /login to the end of the address
@app.route('/')
def go_to_login():
    return redirect(url_for('login'))

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
@flask_login.login_required
def index():
    movie_showtime_data = None
    user_movie_query = None
    error_msg = None
    user_location = "Austin, Texas, United States"
    time_obj = datetime.now()
    user_date = time_obj.strftime("%m/%d/%y")
    if request.method == "POST":
        # validate that user has entered both a zipcode and selected a movie
        if (request.form.get("zipcode-input") == "" 
            or len(request.form.get("zipcode-input")) < 5
            or not request.form.get("zipcode-input").isdigit()):
            error_msg = "ERROR: Zipcode submission error, please enter a valid zipcode"
        elif (request.form.get("selected-movie") == ""):
            error_msg = "ERROR: No movie was selected, please click on Select a Movie and choose a movie!"
        else:
            user_location = zipcode_to_location(request.form.get("zipcode-input"))
            user_movie_query = request.form.get("selected-movie")
            movie_showtime_data = get_showtime_data(user_movie_query, user_location)
        movie_titles, movie_posters, movie_ids = get_movie_details()
        return render_template("index.html",
                                    movie_titles = movie_titles,
                                    movie_posters = movie_posters,
                                    movie_ids = movie_ids,
                                    movie_showtime_data = movie_showtime_data,
                                    user_movie_query = user_movie_query,
                                    user_date = user_date,
                                    user_location = user_location,
                                    error_msg = error_msg)
    else:
        movie_titles, movie_posters, movie_ids = get_movie_details()
    
        return render_template("index.html",
                                    movie_titles = movie_titles,
                                    movie_posters = movie_posters,
                                    movie_ids = movie_ids,
                                    movie_showtime_data = movie_showtime_data,
                                    user_movie_query = user_movie_query,
                                    user_date = user_date,
                                    user_location = user_location,
                                    error_msg = error_msg)

def get_movie_details():
    # Parts of the TMDB URL
    TMDB_BASE_URL = "https://api.themoviedb.org/3"
    TMDB_MOVIE_NOW_PLAYING_PATH = "/movie/now_playing"
    TMDB_POSTER_PREFIX = "http://image.tmdb.org/t/p/w500/"

    get_response = requests.get(
        TMDB_BASE_URL + TMDB_MOVIE_NOW_PLAYING_PATH,
        params={
            "api_key": os.getenv("TMDB_API_KEY"),

        },
    )
    # Store the TMDB JSON in a variable for later use.
    movie_info = get_response.json()
    
    # Making lists to store Now Playing Data
    movie_titles = []
    movie_posters = []
    movie_ids = []

    # Getting now playing movie details from TMDB
    for movie in movie_info["results"]:
        movie_titles.append(movie["title"])
        movie_posters.append(TMDB_POSTER_PREFIX + movie["poster_path"])
        movie_ids.append(movie["id"])

    return movie_titles, movie_posters, movie_ids

app.run(debug=True)

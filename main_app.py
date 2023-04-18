import os
from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def registration():
    return render_template("registration.html")

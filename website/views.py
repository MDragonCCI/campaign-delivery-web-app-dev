from flask import Blueprint, render_template

home = Blueprint('home', __name__)


@home.route("/")
def home_objects():
	return render_template("home.html")
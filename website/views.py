from flask import Blueprint

home = Blueprint('home', __name__)


@home.route("/")
def home_objects():
	return "<h1>Test123</h>"
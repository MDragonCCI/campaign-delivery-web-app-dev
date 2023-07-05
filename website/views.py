from flask import Blueprint, render_template, redirect, url_for, request

home = Blueprint('home', __name__)


@home.route("/", methods=["GET", "POST"])
def home_objects():
	if request.method == "POST":
		return redirect(url_for("revenue.revenue_func"))
	return render_template("home.html")
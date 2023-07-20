from flask import Blueprint, render_template, request, flash, Response,  redirect, url_for, session
import requests
import pandas as pd
import json
from datetime import datetime
import time
import io
import app_config
from .views import _get_token_from_cache
from .scripts import login, proposal_search, campaign_ectractor
 



revenue = Blueprint('revenue', __name__)


@revenue.route('/revenue', methods=["GET", "POST"])
def revenue_func():
	token = _get_token_from_cache(app_config.SCOPE)
	if not token:
		return redirect(url_for("home.login"))
	headers = []
	env = []
	data = request.form
	print(data)
	if request.method == "POST":
		env = request.form.get("env")
		session["env"] = request.form.get("env")
		#start_date = request.form.get("date")
		#end_date = request.form.get("date1")
		email = request.form.get("email")
		#allocation_stats = request.form.get("Allocation_Stats")
		password = request.form.get("password")
		if email == None or password == None:
			flash("Broadsign Login or password is missing. Please try again", category="error")
		else:
			header = login(env, email, password)
			if header is None:
				flash("Login failed. Try egain", category = "error")
			else:
				session["headers"] = header
				return redirect(url_for("revenue.revenue_params"))
			
				
				
				
				
	return render_template("revenue.html")

@revenue.route("revenue/params", methods=["GET", "POST"])
def revenue_params():
	token = _get_token_from_cache(app_config.SCOPE)
	if not token:
		return redirect(url_for("home.login"))
	headers = session.get("headers", None)
	print(headers)
	env = session.get("env", None)
	print(env)
	start_date = []
	end_date = []
	allocation_stats =[]
	if request.method == "POST":
		print(request.form)
		start_date = request.form.get("date")
		end_date = request.form.get("date1")
		allocation_stats = request.form.get("Allocation_Stats")
		print(start_date, end_date)
		if end_date < start_date:
			flash("Start date is grater then end date", category="error")
		elif start_date == "" or end_date == "":
			flash("Date is missing", category = "error")
		else:
			flash("Creation of the report started. It might take few minutes to complite. Please do not refresh the page", category="success")
			search_df = proposal_search(headers, env, start_date, end_date)
			if search_df.empty:
				flash("Search error try again", category = "error")
			else:
				csv_df = campaign_ectractor(headers, env, start_date, end_date, search_df, allocation_stats)
				session["data"] = csv_df.to_json()
				return redirect(url_for("revenue.rev_summary"))
	return render_template("rev_params.html")




@revenue.route("revenue/summary", methods=["GET", "POST"])
def rev_summary():
	token = _get_token_from_cache(app_config.SCOPE)
	if not token:
		return redirect(url_for("home.login"))
	csv_json = session.get("data", None)
	csv_df = pd.read_json(csv_json)
	if request.method == "POST":
		return Response(
       csv_df.to_csv(index = False),
       mimetype="text/csv",
       headers={"Content-disposition":
       "attachment; filename=filename.csv"})
	return render_template("rev_summary.html", tables=[csv_df.to_html(classes='data', index = False)], titles=csv_df.columns.values)





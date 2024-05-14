from flask import Blueprint, render_template, request, flash, Response,  redirect, url_for, session
import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import time
import io
import app_config
from .views import _get_token_from_cache
from .scripts import login
import asyncio
from .email import send_email
import os
from dateutil.relativedelta import relativedelta
from .availibility_func import availibility_checker

PASSWORD = ""


availibility = Blueprint('availibility', __name__)


@availibility.route('/availibility', methods=["GET", "POST"])
def availibility_func():
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
		session["bsd_email"] = email
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
				session["iteration"] = []
				session["is_done"] = 0
				return redirect(url_for("availibility.availibility_params"))
	return render_template("revenue.html")




@availibility.route('/availibility/parmas', methods=["GET", "POST"])
def availibility_params():
	token = _get_token_from_cache(app_config.SCOPE)
	if not token:
		return redirect(url_for("home.login"))
	if request.method == "POST":
		print("Button pressed")
		start_date = datetime.date(datetime.strptime(request.form.get("startDate"), "%Y-%m-%d"))
		session["start_date"] = start_date
		end_date = datetime.date(datetime.strptime(request.form.get("endDate"), "%Y-%m-%d"))
		session["end_date"] = end_date
		duration = request.form.get("duration")
		session["duration"] = duration
		type_of_buy = request.form.get("typeOfBuys")
		session["type_of_buy"] = type_of_buy
		tob_value = request.form.get("additionalValue")
		session["tob_value"] = tob_value
		min_dates = timedelta(days=6)
		date_range = end_date - start_date
		if start_date > end_date:
			flash("Start date is grated then end date", category="error")
		elif date_range < min_dates:
			flash("Date range is lower then 7 days", category="error")
		else:
			results = availibility_checker()
			session["avail_downloads"] = results.to_dict(orient='records')
			table_headers = results.columns.tolist()
			day_1 = table_headers[4]
			day_2 = table_headers[5]
			day_3 = table_headers[6]
			day_4 = table_headers[7]
			day_5 = table_headers[8]
			day_6 = table_headers[9]
			day_7 = table_headers[10]
			results.rename(columns={f"{day_1}": "Day 1", f"{day_2}": "Day 2", f"{day_3}": "Day 3", f"{day_4}": "Day 4", f"{day_5}": "Day 5", f"{day_6}": "Day 6", f"{day_7}": "Day 7"}, inplace=True)
            #print(f"{start_date}, {end_date}, {tob_value}, {duration}, {type_of_buy}")
			print(results)
			
			print(table_headers)
			session["avail_table"] = results.to_dict(orient='records')
			session["col_headers"] = table_headers
			
	return render_template("availibility_params.html")


@availibility.route('/availibility/parmas/download', methods=["GET", "POST"])
def long():
	token = _get_token_from_cache(app_config.SCOPE)
	if not token:
		return redirect(url_for("home.login"))
	csv_df = pd.DataFrame.from_dict(session.get("avail_downloads", None)) 
	file_headers = {"Content-disposition": "attachment; filename=Availibility_checker.csv"}
	print(file_headers)
	return Response(
       csv_df.to_csv(index = False),
       mimetype="text/csv",
       headers=file_headers)
	


			
				
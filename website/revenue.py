from flask import Blueprint, render_template, request, flash, Response,  redirect, url_for, session
import requests
import pandas as pd
import json
from datetime import datetime
import time
import io
import app_config
from .views import _get_token_from_cache
from .scripts import login, proposal_search, campaign_ectractor,  run_campaign_extractor
import asyncio
 



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
				session["iteration"] = []
				session["is_done"] = 0
				return redirect(url_for("revenue.revenue_params"))
			
				
				
				
				
	return render_template("revenue.html")



@revenue.route("revenue/params", methods=["GET", "POST"])
def revenue_params():
	token = _get_token_from_cache(app_config.SCOPE)
	if not token:
		return redirect(url_for("home.login"))
	#headers = session.get("headers", None)
	
	#env = session.get("env", None)
	
	start_date = []
	end_date = []
	#allocation_stats =[]
	
	if request.method == "POST":
		print(request.form)
		#start_date = request.form.get("date")
		#end_date = request.form.get("date1")
		session["allocation_stats"] = request.form.get("Allocation_Stats")
		session["submitted"] = request.form.get("Submitted")
		session["booked"] = request.form.get("Booked")
		session["ended"] = request.form.get("Ended")
		session["hold"] = request.form.get("Hold")
		session["preempt"] = request.form.get("preempt")
		session["start_date"] = request.form.get("date")
		session["end_date"] = request.form.get("date1")
		session["temp_json"] = []
		print(start_date, end_date)
		if end_date < start_date:
			flash("Start date is grater then end date", category="error")
		elif start_date == "" or end_date == "":
			flash("Date is missing", category = "error")
		else:
			flash("Creation of the report started. It might take few minutes to complite. Please do not refresh the page", category="success")
			search_df = proposal_search()
			n = len(search_df)
			session["proposal_total_numbers"] = n
			session["proposal_done"] = 0
			iteration = [i for i in range(0, n)]
			session["iteration"] = iteration
			search_json = search_df.to_json()
			print(search_df)
			if search_df is None:
				flash("Search error try again", category = "error")
			else:
				#campaign_ectractor(headers, env, start_date, end_date, search_df, allocation_stats)
				#session["data"] = csv_df.to_json()
				#print(session.get("temp_json"))
				#if  __name__ == "__main__":
				#asyncio.run(run_campaign_extractor(search_df, allocation_stats))
				session["is_done"] = 1
				session["search_json"] = search_json
				print(session.get("search_df"))
				return redirect(url_for("revenue.revenue_waiting"))
	return render_template("rev_params.html")



@revenue.route("revenue/waiting", methods=["GET"])
def revenue_waiting():
	token = _get_token_from_cache(app_config.SCOPE)
	if not token:
		return redirect(url_for("home.login"))
	#headers = session.get("headers", None)
	
	#env = session.get("env", None)
	
	#allocation_stats =[]
	if len(session.get("iteration")) == 0 and session.get("is_done") == 1:
		return redirect(url_for("revenue.rev_summary"))
	else:
		if len(session.get("iteration")) < 50:
			N = len(session.get("iteration"))
		else:
			N = 10
		result = []
		session["proposal_done"] = session.get("proposal_done") + N
		for index in range(N):
			result.append(session.get("iteration")[index])
		for index in range(N):
			opped_item = session.get("iteration").pop(0)
		print(session.get("iteration"))
		print(type(result))
		print(type(result))
		asyncio.run(run_campaign_extractor(result))
	#proposal_total_numbers = session.get("proposal_total_numbers")
	#proposal_done = session.get("proposal_done")
	session["proposal_progress"] = session.get("proposal_done")*100/session.get("proposal_total_numbers")
	#proposal_done = session.get("proposal_done")
	csv_json = session.get("temp_json", None)
	csv_df = pd.DataFrame.from_dict(csv_json)	
	return render_template("revenue_waiting.html", tables=[csv_df.to_html(classes='data', index = False)], titles=csv_df.columns.values)


@revenue.route("revenue/summary", methods=["GET", "POST"])
def rev_summary():
	token = _get_token_from_cache(app_config.SCOPE)
	if not token:
		return redirect(url_for("home.login"))
	csv_json = session.get("temp_json", None)
	csv_df = pd.DataFrame.from_dict(csv_json)
	if request.method == "POST":
		return Response(
       csv_df.to_csv(index = False),
       mimetype="text/csv",
       headers={"Content-disposition":
       "attachment; filename=filename.csv"})
	return render_template("rev_summary.html", tables=[csv_df.to_html(classes='data', index = False)], titles=csv_df.columns.values)





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
from .email import send_email
import os
from dateutil.relativedelta import relativedelta

PASSWORD = ""


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
		#print(request.form)
		start_date = request.form.get("date")
		end_date = request.form.get("date1")
		print(type(start_date), end_date)
		session["allocation_stats"] = request.form.get("Allocation_Stats")
		session["submitted"] = request.form.get("Submitted")
		session["booked"] = request.form.get("Booked")
		session["ended"] = request.form.get("Ended")
		session["hold"] = request.form.get("Hold")
		session["preempt"] = request.form.get("preempt")
		session["start_date"] = request.form.get("date")
		session["end_date"] = request.form.get("date1")
		print(type(session.get("preempt", None)))
		print(start_date, end_date)
		if end_date < start_date:
			flash("Start date is grater then end date", category="error")
		elif request.form.get("date1") == "" or request.form.get("date") == "":
			flash("Dates are missing", category = "error")
		else:
			flash("Creation of the report started. It might take few minutes to complete. Please do not refresh the page", category="success")
			session["ce_last_run"] = None
			session["temp_json"] = []
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
	
	N = 10
	EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
	if len(session.get("iteration")) == 0 and session.get("is_done") == 1:
		session["ce_last_run"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
		session["ce_created"] = time.strftime("%Y%m%d_%H%M%S")
		user = session.get("user", None)
		subject = "Campaign extractor notification "+str(session.get("ce_last_run", None))
		body = "Campaign extractor has been trigered by "+user.get("name")+" and genertetd the report at: "+str(session.get("ce_last_run", None))
		sender = "campaign.delivery.notification@gmail.com"
		recipients = ["michal.dragon@clearchannel.co.uk"]
		password = EMAIL_PASSWORD
		send_email(subject, body, sender, recipients, password)
		return redirect(url_for("revenue.rev_summary"))
	else:
		if len(session.get("iteration")) < N:
			N = len(session.get("iteration"))
		else:
			pass
		result = []
		session["proposal_done"] = session.get("proposal_done") + N
		for index in range(N):
			result.append(session.get("iteration")[index])
		for index in range(N):
			poped_item = session.get("iteration").pop(0)
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
	session["campaign_extractor"] = csv_df.to_dict(orient='records')
	# Statuses char
	statuses_df = csv_df.groupby(["PLI Status"])["PLI Status"].count()
	print(statuses_df)
	statuses = statuses_df.to_dict()
	if "Booked" in statuses:
		session["Booked_num"] = (statuses.get("Booked"))
	else:
		session["Booked_num"] = 0

	if "Live" in statuses:
		session["Live_num"] = (statuses.get("Live"))
	else:
		session["Live_num"] = 0

	if "Submitted" in statuses:
		session["Submitted_num"] = (statuses.get("Submitted"))
	else:
		session["Submitted_num"] = 0

	if "Ended" in statuses:
		session["Ended_num"] = (statuses.get("Ended"))
	else:
		session["Ended_num"] = 0

	if "Held" in statuses:
		session["Held_num"] = (statuses.get("Held"))
	else:
		session["Held_num"] = 0

	camp_over_perf = pd.DataFrame.from_dict(csv_json)
	camp_on_target = pd.DataFrame.from_dict(csv_json)
	camp_under_perf = pd.DataFrame.from_dict(csv_json)
	camp_long = pd.DataFrame.from_dict(csv_json)
	to_drop_over = []
	to_drop_under = []
	to_drop_target = []
	to_drop_long = []
	for i in range(0, len(csv_df)):
		camp_perf = csv_df.iloc[i]["Campaign Performance %"]
		pli_start_date = csv_df.iloc[i]["Start date"]
		pli_end_date = csv_df.iloc[i]["End date"]
		pli_start_date = datetime.date(datetime.strptime(pli_start_date, "%Y-%m-%d"))
		pli_end_date = datetime.date(datetime.strptime(pli_end_date, "%Y-%m-%d"))
		long = datetime.date(datetime.strptime("2023-05-31", "%Y-%m-%d")) - datetime.date(datetime.strptime("2023-05-01", "%Y-%m-%d"))
		print(long)
		delta = pli_end_date - pli_start_date
		if delta > long:
			to_drop_over.append(i)
			to_drop_under.append(i)
		elif delta < long:
			to_drop_long.append(i)
		else:
			pass

		if camp_perf == "N/A" or camp_perf is None:
			to_drop_over.append(i)
			to_drop_target.append(i)
			to_drop_under.append(i)
			to_drop_long.append(i)
			#print(camp_perf)
		elif camp_perf <= 90:
			to_drop_over.append(i)
			to_drop_target.append(i)
			#print(camp_perf)
		elif camp_perf >= 110:
			to_drop_target.append(i)
			to_drop_under.append(i)
		elif camp_perf > 90 and camp_perf < 110:
			to_drop_over.append(i)
			to_drop_under.append(i)
			to_drop_long.append(i)
		else:
			to_drop_over.append(i)
			to_drop_target.append(i)
			to_drop_under.append(i)
			to_drop_long.append(i)
			#print(camp_perf)
	#print(to_drop_over)
	#print(to_drop_target)
	
	camp_over_perf.drop(camp_over_perf.index[to_drop_over], inplace = True)
	#print(camp_over_perf)
	camp_under_perf.drop(camp_under_perf.index[to_drop_under], inplace = True)
	#print(camp_under_perf)
	camp_on_target.drop(camp_on_target.index[to_drop_target], inplace = True)
	#print(camp_on_target)
	camp_long.drop(camp_long.index[to_drop_long], inplace = True)
	
	
	camp_over_dict = camp_over_perf.to_dict(orient='records')
	session["camp_over"] = camp_over_dict
	session["camp_over_number"] = len(camp_over_perf)

	camp_under_dict = camp_under_perf.to_dict(orient='records')
	session["camp_under"] = camp_under_dict
	session["camp_under_number"] = len(camp_under_perf)

	camp_target_dict = camp_on_target.to_dict(orient='records')
	session["camp_target"] = camp_target_dict
	session["camp_target_number"] = len(camp_on_target)

	camp_long_dict = camp_long.to_dict(orient='records')
	session["camp_long"] = camp_long_dict
	session["camp_long_number"] = len(camp_long)



	if request.method == "POST":
		last_run = session.get("ce_created")
		file_headers = {"Content-disposition": "attachment; filename=campaign_extractor_report_"+str(last_run)+".csv"}
		print(file_headers)
		return Response(
       csv_df.to_csv(index = False),
       mimetype="text/csv",
       headers=file_headers)
	return render_template("rev_summary.html")

@revenue.route("revenue/over", methods=["GET", "POST"])
def over():
	token = _get_token_from_cache(app_config.SCOPE)
	if not token:
		return redirect(url_for("home.login"))
	csv_df = pd.DataFrame.from_dict(session.get("camp_over", None)) 
	if request.method == "POST":
		last_run = session.get("ce_created")
		file_headers = {"Content-disposition": "attachment; filename=campaign_extractor_overperformance_report_"+str(last_run)+".csv"}
		print(file_headers)
		return Response(
       csv_df.to_csv(index = False),
       mimetype="text/csv",
       headers=file_headers)
	return render_template("camp_over.html")

@revenue.route("revenue/under", methods=["GET", "POST"])
def under():
	token = _get_token_from_cache(app_config.SCOPE)
	if not token:
		return redirect(url_for("home.login"))
	csv_df = pd.DataFrame.from_dict(session.get("camp_under", None)) 
	if request.method == "POST":
		last_run = session.get("ce_created")
		file_headers = {"Content-disposition": "attachment; filename=campaign_extractor_underperformance_report_"+str(last_run)+".csv"}
		print(file_headers)
		return Response(
       csv_df.to_csv(index = False),
       mimetype="text/csv",
       headers=file_headers)
	return render_template("camp_under.html")

@revenue.route("revenue/target", methods=["GET", "POST"])
def target():
	token = _get_token_from_cache(app_config.SCOPE)
	if not token:
		return redirect(url_for("home.login"))
	csv_df = pd.DataFrame.from_dict(session.get("camp_target", None)) 
	if request.method == "POST":
		last_run = session.get("ce_created")
		file_headers = {"Content-disposition": "attachment; filename=campaign_extractor_on_target_report_"+str(last_run)+".csv"}
		print(file_headers)
		return Response(
       csv_df.to_csv(index = False),
       mimetype="text/csv",
       headers=file_headers)
	return render_template("camp_target.html")



@revenue.route("revenue/long", methods=["GET", "POST"])
def long():
	token = _get_token_from_cache(app_config.SCOPE)
	if not token:
		return redirect(url_for("home.login"))
	csv_df = pd.DataFrame.from_dict(session.get("camp_long", None)) 
	if request.method == "POST":
		last_run = session.get("ce_created")
		file_headers = {"Content-disposition": "attachment; filename=campaign_extractor_long_campaigns_report_"+str(last_run)+".csv"}
		print(file_headers)
		return Response(
       csv_df.to_csv(index = False),
       mimetype="text/csv",
       headers=file_headers)
	return render_template("camp_long.html")







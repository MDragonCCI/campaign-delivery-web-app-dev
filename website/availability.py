from flask import Blueprint, render_template, request, flash, Response,  redirect, url_for, session
import requests
import pandas as pd
from datetime import datetime, timedelta
import app_config
from .views import _get_token_from_cache
from .scripts import login
from .email_func import send_email
from dateutil.relativedelta import relativedelta
from .availability_func import availability_checker
import os

PASSWORD = ""

# Blueprint registration
availability = Blueprint('availability', __name__)
BSD_LOGIN = os.getenv("BSD_LOGIN")
BSD_PASSWORD = os.getenv("BSD_PASSWORD")


#Rout for BS Direct login 
@availability.route('/availability', methods=["GET", "POST"])
def availability_func():
	token = _get_token_from_cache(app_config.SCOPE)
	if not token:
		return redirect(url_for("home.login"))
	
	#Clear env var
	env = []
	print(type(BSD_PASSWORD))
	#Capture data from fronend once the form is submitted
	if request.method == "POST":
		
		#Pull data from frontend form and assign them to the vars and session's var
		env = request.form.get("env")
		session["env"] = request.form.get("env")
		email = request.form.get("email")
		session["bsd_email"] = email
		password = request.form.get("password")
		
		#Validation for credentials
		if email == None or password == None:
			flash("Broadsign Login or password is missing. Please try again", category="error")
		else:
			#Call login function to capture BS Direct token
			header = login(env, email, password)
			
			#Valiudation if the login has been complited
			if header is None:
				flash("Login failed. Try egain", category = "error")
				return render_template("revenue.html")
			else:
				#Token has been captured. Save it in vars and redirect to the next page
				session["headers"] = header
				return redirect(url_for("availability.availibility_params"))
	if BSD_LOGIN != None and BSD_PASSWORD != None:
		env = "https://direct.broadsign.com/"
		email = BSD_LOGIN
		password = BSD_PASSWORD
		header = login(env, email, password)
		#Valiudation if the login has been complited
		if header is None:
			flash("Login failed. Try egain", category = "error")
			pass
		else:
			#Token has been captured. Save it in vars and redirect to the next page
			session["headers"] = header
			session["env"] = env
			return redirect(url_for("availability.availibility_params"))
	else:
		pass
	return render_template("revenue.html")
	



#Availibility page
@availability.route('/availability/parmas', methods=["GET", "POST"])
def availibility_params():
	token = _get_token_from_cache(app_config.SCOPE)
	if not token:
		return redirect(url_for("home.login"))
	headers = session.get("headers", None)
	if headers == None:
		return redirect("availability.availibility_func")
	#Condition to capture the data from the UI
	if request.method == "POST":
		print("Button pressed")
		
		#Save the data from UI into the vars
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
		#Validation for the dates in UI
		#Minimuym range allowed is 7 days. To change it change the value of min_dates var
		min_dates = timedelta(days=6)
		
		#Calculate date range
		date_range = end_date - start_date
		
		#Validation checkes i.e if the start date is > then the end date
		if start_date > end_date:
			flash("Start date is grated then end date", category="error")
		
		#Validation to check if the date range is at least 7 days
		elif date_range < min_dates:
			flash("Date range is lower then 7 days", category="error")
		
		#If the dates pass the validation procces to check availability
		else:
			#Call availibility function
			results = availability_checker()
			#Save resuylkt into the session var to use it for download CSV
			session["avail_downloads"] = results.to_dict(orient='records')
			
			
			
			#Take table headers for UI
			table_headers = results.columns.tolist()
			print(table_headers)
			#Prepare data for the UI preview for first 7 days
			day_1 = table_headers[8]
			day_2 = table_headers[9]
			day_3 = table_headers[10]
			day_4 = table_headers[11]
			day_5 = table_headers[12]
			day_6 = table_headers[13]
			day_7 = table_headers[14]
			#Update the names of the first 7 days to map them in UI
			results.rename(columns={f"{day_1}": "Day 1", f"{day_2}": "Day 2", f"{day_3}": "Day 3", f"{day_4}": "Day 4", f"{day_5}": "Day 5", f"{day_6}": "Day 6", f"{day_7}": "Day 7"}, inplace=True)
            #print(f"{start_date}, {end_date}, {tob_value}, {duration}, {type_of_buy}")
			print(results)
			#print(table_headers)
			#print(pd. __version__) 
			
			#Save data to session vars to display them in UI
			session["avail_table"] = results.to_dict(orient='records')
			session["col_headers"] = table_headers
			
	return render_template("availability_params.html")


#Download report in CSV format
@availability.route('/availability/parmas/download', methods=["GET", "POST"])
def download():
	token = _get_token_from_cache(app_config.SCOPE)
	if not token:
		return redirect(url_for("home.login"))
	#Pull data from seession varable to DF
	csv_df = pd.DataFrame.from_dict(session.get("avail_downloads", None)) 
	#Add file parameters
	file_headers = {"Content-disposition": "attachment; filename=Availability_checker.csv"}
	#print(file_headers)
	return Response(
       csv_df.to_csv(index = False),
       mimetype="text/csv",
       headers=file_headers)
	


			
				
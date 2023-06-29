from flask import Blueprint, render_template, request, flash, Response
import requests
import pandas as pd
import json


revenue = Blueprint('revenue', __name__)
revenue_report = Blueprint('revenue_report', __name__)

@revenue.route('/revenue', methods=["GET", "POST"])
def revenue_func():
	data = request.form
	print(data)
	if request.method == "POST":
		global headers
		global start_date
		global end_date
		global env
		env = request.form.get("env")
		start_date = request.form.get("date")
		end_date = request.form.get("date1")
		email = request.form.get("email")
		password = request.form.get("password")
		loginpage = env+"/login"
		credentials={
    "email": [str(email)],
    "password": [str(password)]
    }
		print(start_date, end_date)
		if end_date < start_date:
			flash("Start date is grater then end date", category="error")
		else:
			login = requests.request("POST", url=loginpage, headers={}, data=credentials, files=[])
			if login.status_code == 200:
				flash("Login sucess", category="success")
				token= "session="+login.cookies["session"]
				headers = {"Cookie": token}
				revenue_search_script()
			else:
				flash("Login failed. Check your credentials and try again", category="error")
	return render_template("revenue.html") 

def revenue_search_script():
	global headers
	global env
	global search_df
	print(headers, start_date, end_date, env)
	search_url = env+"api/v1/proposal/search"
	print(search_url)
	search_pl = json.dumps({
  "$top": 10000,
  "$skip": 0,
  "$sort": [
    {
      "field": "last_modification_date_time",
      "dir": "desc"
    }
  ],
  "status": ["live", "held", "submitted", "ended", "booked",
  "partially_held"],
  "keyword": "",
  "only_user": False,
  "date": str("2023-06-26")
})
	search = requests.request("POST", url=search_url, headers=headers, data=search_pl)
	if search.status_code == 200:
		search_df = pd.DataFrame.from_dict(search.json()["data"])
		revenue_pli_script()
		#print(df)
	else:
		flash("Broadsign Direct Search ERROR", category = "error")


def revenue_pli_script():
	global search_df
	global start_date
	global end_date
	global headers
	
	return Response(
       search_df.to_csv(),
       mimetype="text/csv",
       headers={"Content-disposition":
       "attachment; filename=filename.csv"})
#print(search_df)

@revenue_report.route('/revenue/report', methods=["GET", "POST"])
def revenue_func():
	global search_df
	global start_date
	global end_date
	global headers
	
	return Response(
       search_df.to_csv(index = False),
       mimetype="text/csv",
       headers={"Content-disposition":
       "attachment; filename=filename.csv"})
#print(search_df)




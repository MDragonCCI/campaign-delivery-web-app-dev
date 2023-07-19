from flask import Blueprint, render_template, request, flash, Response,  redirect, url_for
import requests
import pandas as pd
import json
from datetime import datetime
import time
import io
import app_config
from .views import _get_token_from_cache



revenue = Blueprint('revenue', __name__)


@revenue.route('/revenue', methods=["GET", "POST"])
def revenue_func():
	token = _get_token_from_cache(app_config.SCOPE)
	if not token:
		return redirect(url_for("home.login"))
	global headers
	global env
	headers = []
	env = []
	data = request.form
	print(data)
	if request.method == "POST":
		env = request.form.get("env")
		start_date = request.form.get("date")
		end_date = request.form.get("date1")
		email = request.form.get("email")
		allocation_stats = request.form.get("Allocation_Stats")
		password = request.form.get("password")
		loginpage = env+"/login"
		credentials={
    "email": [str(email)],
    "password": [str(password)]
    }
		print(start_date, end_date)
		if email == None or password == None:
			flash("Broadsign Login or password is missing. Please try again", category="error")
		else:
			login = requests.request("POST", url=loginpage, headers={}, data=credentials, files=[])
			if login.status_code == 200:
				flash("Login successful!", category="success")
				token1= "session="+login.cookies["session"]
				headers = {"Cookie": token1}
				return redirect(url_for("revenue.revenue_params"))
			else:
				flash("Login failed. Check your credentials and try again", category="error")
				print(allocation_stats)
				
				
				
	return render_template("revenue.html")

@revenue.route("revenue/params", methods=["GET", "POST"])
def revenue_params():
	global start_date
	global end_date
	global allocation_stats
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
			return redirect(url_for("revenue.revenue_search"))
	return render_template("rev_params.html")



@revenue.route('/revenue/search', methods=["GET", "POST"])
def revenue_search():
	global headers
	global search_df
	search_df = []
	print(headers)
	search_url = env+"api/v1/proposal/search"
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
	if 1==1:
		search = requests.request("POST", url=search_url, headers=headers, data=search_pl)
		if search.status_code == 200:
			search_df = pd.DataFrame.from_dict(search.json()["data"])
			return redirect(url_for("revenue.revenue_pli"))
		else:
			flash("Broadsign Direct Search ERROR", category = "error")

	return render_template("waiting.html")

@revenue.route('/revenue/processing', methods=["GET", "POST"])
def revenue_pli():
	global start_date
	global end_date
	global search_df
	global headers
	global allocation_stats
	global env
	global csv_df
	if allocation_stats != None:
		allocation_stats = 1
	else:
		allocation_stats = 0
	csv_data = {
    "proposal id": [],
    "proposal name": [],
     "PLI ID": [],
    "PLI Name": [],
    "TOB": [],
    "Sub Type": [],
    "Number of screens": [],
    "Creation Time": [],
    "Actual Imp": [],
    "Actual Rep": [],
    "Expected_impressions": [],
    "Expected_repetitions": [],
	"Expected today": [],
    "Campaign Performance %": [],
    "Imp/Rep goal": [],
    "SoV goal": [],
    "Saturation": [],
    "Imp Boundary": [],
    "Av. SoV lower boundary": [],
    "Av. SoV upper boundary": [],
    "Av. SoV": [],
    "PLI Status": [],
    "Start date": [],
    "start time": [],
    "End date": [],
    "End time": [],
    "DoW mask": [],
    "BSC ID": [],
    "Priority": [],
    "Is pre-empt": [],
    "Performance update": [],
    "Auto Rebalance": [],
    "Booking time": [],
    "Allocation St. Dev": [],
    "Allocation Av. Saturation": []
}
	csv_df = pd.DataFrame(csv_data)

	for index in range(0, len(search_df)):
		proposal_id = search_df.iloc[index]["id"]
		proposal_name = search_df.iloc[index]["name"]
		proposal_start = search_df.iloc[index]["start_date"]
		proposal_end = search_df.iloc[index]["end_date"]
		proposal_status = search_df.iloc[index]["status"]
		proposal_start_dt = datetime.date(datetime.strptime(proposal_start, "%Y-%m-%d"))
		proposal_end_dt = datetime.date(datetime.strptime(proposal_end, "%Y-%m-%d"))
		start_date = datetime.date(datetime.strptime(str(start_date), "%Y-%m-%d"))
		end_date = datetime.date(datetime.strptime(str(end_date), "%Y-%m-%d"))
		#print(type(start_date))
		#print(type(proposal_start_dt))
		if proposal_status == 11 and start_date >= proposal_end_dt:
			print("skip "+ str(proposal_id), str(proposal_status), str(proposal_end_dt))
		elif start_date <= proposal_start_dt and end_date >= proposal_start_dt or proposal_status == 11 and start_date >= proposal_start_dt or proposal_status == 14 and start_date <= proposal_end_dt and end_date >= proposal_end_dt:
			pli_url = env+"api/v1/proposal/"+str(proposal_id)+"/proposal_items"
			pli = requests.request("POST", url=pli_url, headers=headers, data=[])
			if pli.status_code == 200:
				pli_df = pd.DataFrame.from_dict(pli.json()["data"])
				for index2 in range(0, len(pli_df)):
					mode_df = pd.DataFrame.from_dict(pli_df.iloc[index2]["mode"])
					tob_df = mode_df[mode_df["active"]!=False]
					pli_tob_values = tob_df.iloc[0]["values"]
					pli_type = tob_df.iloc[0]["type"]
					pli_boundary = "N/A"
					pli_id = pli_df.iloc[index2]["id"]
					pli_name = pli_df.iloc[index2]["name"]
					pli_tob = pli_df.iloc[index2]["active_type"]
					pli_cr_tm = pli_df.iloc[index2]["creation_tm"]
					pli_act_imp = pli_df.iloc[index2]["actual_impressions"]
					pli_act_rep = pli_df.iloc[index2]["actual_repetitions"]
					pli_perf_update = pli_df.iloc[index2]["performance_update_tm"]
					pli_target = pli_df.iloc[index2]["target"]
					pli_status_id = pli_df.iloc[index2]["status"]
					pli_start_dt = pli_df.iloc[index2]["start_date"]
					pli_end_dt = pli_df.iloc[index2]["end_date"]
					pli_end =  datetime.date(datetime.strptime(pli_end_dt, "%Y-%m-%d"))
					pli_start_tm = pli_df.iloc[index2]["start_time"]
					pli_end_tm = pli_df.iloc[index2]["end_time"]
					pli_dow = pli_df.iloc[index2]["dow_mask"]
					pli_bsc_id = pli_df.iloc[index2]["provider_id"]
					try:
						pli_tob_values["saturation"]
					except NameError:
						pli_saturation = "N/A"
					except KeyError:
						pli_saturation = "N/A"
					else:
						pli_saturation = pli_tob_values["saturation"]
					try:
						pli_tob_values["distribution"]
					except NameError:
						pli_tob_s = "N/A"
					except KeyError:
						pli_tob_sub = "N/A"
					else:
						pli_tob_sub = pli_tob_values["distribution"]
					pli_prio = pli_df.iloc[index2]["priority"]
					pli_is_preempt_raw = pli_df.iloc[index2]["is_preemptible"]
					if pli_is_preempt_raw != True:
						if pli_status_id == 11 and pli_perf_update != None:
							pli_perf_actual = (pli_df.iloc[index2]["performance"])["actual"]
							pli_perf_projected = (pli_df.iloc[index2]["performance"])["projected"]
                        

							if pli_perf_actual < 1 or pli_perf_projected < 1:
								pli_cp = "N/A"
								pli_perf_projected = "N/A"
							else:
								pli_perf_update_tm = datetime.time(datetime.strptime(str(pli_perf_update), "%Y-%m-%d %H:%M:%S"))
								pli_perf_update_dt =  datetime.date(datetime.strptime(str(pli_perf_update), "%Y-%m-%d %H:%M:%S"))
								pli_start_dt = datetime.date(datetime.strptime(str(pli_start_dt), "%Y-%m-%d"))
								delta_days = pli_perf_update_dt -pli_start_dt
								delta_days = delta_days.days
								print(delta_days, proposal_id, pli_start_dt, pli_perf_update, pli_perf_actual, pli_perf_projected)
								if delta_days < 1:
									delta_days = 1
									aprox_daily = pli_perf_projected / (delta_days)
								else:
									aprox_daily = pli_perf_projected / (delta_days+1)
								up_till_today = aprox_daily * delta_days
								pli_perf_update_tm= str(pli_perf_update_tm).split(':')
								x=list(map(int,pli_perf_update_tm))
								today_top_up = ((x[0]*60 + x[1]))/1440 * aprox_daily
								pli_cp = round(pli_perf_actual / (up_till_today + today_top_up)* 100,0)
						else:
							pli_cp = "N/A"
							pli_perf_projected = "N/A"

						if (pli_status_id == 9 and allocation_stats == 1) or (pli_status_id == 10 and allocation_stats == 1) or (pli_status_id == 11 and allocation_stats == 1):
							playout_url = env+"api/v1/proposal/proposal_item/"+str(pli_id)+"/playout/csv"
							playout = requests.request("GET", url = playout_url, headers=headers, data=[])
							if playout.status_code == 200:
								r = playout.content
								try:
									df1 = pd.read_csv(io.StringIO(r.decode('utf-8')))
								except NameError:
									pli_std = "N/A"
									pli_mean = "N/A"
								except pd.errors.EmptyDataError:
									pli_std = "N/A"
									pli_mean = "N/A"
								else:
									df1 = pd.read_csv(io.StringIO(r.decode('utf-8')))
									try:
										df1.loc[df1['average_saturation']== -1, 'average_saturation' ] =0
									except NameError:
										pli_std = "N/A"
										pli_mean = "N/A"
									except KeyError:
										pli_std = "N/A"
										pli_mean = "N/A"
									else:
										df1.loc[df1['average_saturation']== -1, 'average_saturation' ] =0
                        
										df1_s_m = df1.average_saturation.agg(['std','mean'])
                        
										pli_std = round(df1_s_m["std"],4)
										pli_mean = round(df1_s_m["mean"],4)
						else:
							pli_std = "N/A"
							pli_mean = "N/A"
						pli_is_preempt = "FALSE"
						try:
							pli_tob_values["goal_impressions_upper_boundary"]
						except NameError:
							pli_imp_boundary = "N/A"
						except KeyError:
							pli_imp_boundary = "N/A"
						else:
							pli_imp_boundary = pli_tob_values["goal_impressions_upper_boundary"]
                    
						try:
							pli_tob_values["expected_repetitions"]
						except NameError:
							pli_expect_rep = "N/A"
						except KeyError:
							pli_expect_rep = "N/A"
						else:
							pli_expect_rep = pli_tob_values["expected_repetitions"]
						try:
							pli_tob_values["expected_impressions"]
						except NameError:
							pli_expect_imp = "N/A"
						except KeyError:
							pli_expect_imp = "N/A"
						else:
							pli_expect_imp = pli_tob_values["expected_impressions"]
                        
						try:
							pli_tob_values["average_sov_lower_boundary"]
						except NameError:
							pli_av_sov_l_boundary = "N/A"
						except KeyError:
							pli_av_sov_l_boundary = "N/A"
						else:
							pli_av_sov_l_boundary = pli_tob_values["average_sov_lower_boundary"]
                            
						try:
							pli_tob_values["average_sov_upper_boundary"]
						except NameError:
							pli_av_sov_u_boundary = "N/A"
						except KeyError:
							pli_av_sov_u_boundary = "N/A"
						else:
							pli_av_sov_u_boundary = pli_tob_values["average_sov_upper_boundary"]
                     
						try:
							pli_tob_values["average_sov"]
						except NameError:
							pli_av_sov = "N/A"
						except KeyError:
							pli_av_sov = "N/A"
						else:
							pli_av_sov = pli_tob_values["average_sov"]
					else:
						pli_is_preempt = "TRUE"
						pli_expect_rep = "N/A"
						pli_expect_imp = "N/A"
						pli_target = "N/A"
						pli_boundary = "N/A"
						pli_av_sov = "N/A"
						pli_av_sov_l_boundary = "N/A"
						pli_av_sov_u_boundary = "N/A"
						pli_imp_boundary = "N/A"
						pli_std = "N/A"
						pli_mean = "N/A"
						pli_cp = "N/A"
						pli_perf_projected = "N/A"
                    
					
					pli_auto_reb = pli_df.iloc[index2]["last_auto_rebalance_tm"]
					pli_no_of_screens = pli_df.iloc[index2]["screen_count"]
					pli_booking_tm = pli_df.iloc[index2]["booking_tm"]
					if str(pli_type) == "average_sov" or str(pli_type) == "sov":
						pli_sov = pli_tob_values["sov"]
						#upper_boundary =
						#lower_boundary = 
						#pli_boundary = lower_boundary, upper_bounday
					else:
						pli_sov = "N/A"
					#Status translation
					if pli_status_id == 10:
						pli_status = "Submitted"
					elif pli_status_id == 11:
						pli_status = "Live"
					elif pli_status_id == 9:
						pli_status = "Booked"
					elif pli_status_id == 14:
						pli_status = "Ended"
					elif pli_status_id == 4:
						pli_status = "Hold"
					else:
						pli_status = "Other "+str(pli_status_id)
					csv_row = {
    "proposal id": proposal_id,
    "proposal name": proposal_name,
    "PLI ID": pli_id,
    "PLI Name": pli_name,
    "TOB": pli_tob,
    "Sub Type": pli_tob_sub,
    "Number of screens": pli_no_of_screens,
    "Creation Time": pli_cr_tm,
    "Actual Imp": pli_act_imp,
    "Actual Rep": pli_act_rep,
    "Expected_impressions": pli_expect_rep,
    "Expected today": pli_perf_projected,
    "Campaign Performance %": pli_cp,
    "Expected_repetitions": pli_expect_imp,
     "Imp/Rep goal": pli_target,
    "SoV goal": pli_sov,
    "Saturation": pli_saturation,
    "Imp Boundary": pli_imp_boundary,
    "Av. SoV lower boundary":  pli_av_sov_l_boundary,
    "Av. SoV upper boundary": pli_av_sov_u_boundary,
    "Av. SoV": pli_av_sov,
    "PLI Status": pli_status,
    "Start date": pli_start_dt,
    "start time": pli_start_tm,
    "End date": pli_end_dt,
    "End time": pli_end_tm,
    "DoW mask": pli_dow,
    "BSC ID": pli_bsc_id,
    "Priority": pli_prio,
    "Is pre-empt": pli_is_preempt,
    "Performance update": pli_perf_update,
    "Auto Rebalance": pli_auto_reb,
    "Booking time": pli_booking_tm,
    "Allocation St. Dev": pli_std,
    "Allocation Av. Saturation": pli_mean
}
					if pli_status_id == 1 and pli_status_id == 12:
						print(csv_row)
					elif pli_status_id == 14 and start_date >= pli_end:
						print(csv_row)
					elif pli_status_id != 1 and pli_status_id != 12:
						csv_df.loc[len(csv_df)] = csv_row
						print(csv_row)
				 
                    
                    
                    
			else:
				flash("Broadsign Direct Search ERROR", category = "error")
	if 1==1:
		return redirect(url_for("revenue.rev_summary"))
	else:
		flash("Something went wrong please try again", category = "error")
	
	return render_template("waiting.html")

@revenue.route("revenue/summary", methods=["GET", "POST"])
def rev_summary():
	global csv_df
	if request.method == "POST":
		return Response(
       csv_df.to_csv(index = False),
       mimetype="text/csv",
       headers={"Content-disposition":
       "attachment; filename=filename.csv"})
	return render_template("rev_summary.html", tables=[csv_df.to_html(classes='data')], titles=csv_df.columns.values)





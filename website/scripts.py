import requests
import pandas as pd
import json
from datetime import datetime
import time
import io
from flask import flash, session
import asyncio






def login(env, email, password):
	loginpage = env+"/login"
	credentials={
    "email": [str(email)],
    "password": [str(password)]
    }
	login = requests.request("POST", url=loginpage, headers={}, data=credentials, files=[])
	if login.status_code == 200:
		flash("Login successful!", category="success")
		token1= "session="+login.cookies["session"]
		headers = {"Cookie": token1}
		return headers
	else:
		flash("Login failed. Check your credentials and try again", category="error")
		return 
				
				
			



def proposal_search():
	#start_date = session.get("start_date", None)
	headers = session.get("headers", None)
	env = session.get("env", None)
	#end_date = session.get("end_date", None)
	search_df = []
	submitted = session.get("submitted", None)
	booked = session.get("booked", None)
	ended = session.get("ended", None)
	hold = session.get("hold", None)
	saved = session.get("saved", None)
	preempt = session.get("preempt", None)
	start_date = session.get("start_date", None)
	end_date = session.get("end_date", None)
	status = ["live"]
	if submitted != None:
		status.append("submitted")
	if booked != None:
		status.append("booked")
	if ended != None:
		status.append("ended")
	if hold != None:
		status.append("held")
		status.append("partially_held")
	if saved != None:
		status.append("saved")
		status.append("cancelled")
		status.append("cancelling")
	

	
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
  "status":status,
  "keyword": "",
  "only_user": False
})

	search = requests.request("POST", url=search_url, headers=headers, data=search_pl)
	if search.status_code == 200:
		search_df = pd.DataFrame.from_dict(search.json()["data"])
		to_drop = []
		for i in range(0, len(search_df)):
			proposal_id = search_df.iloc[i]["id"]
			proposal_start = search_df.iloc[i]["start_date"]
			proposal_end = search_df.iloc[i]["end_date"]
			proposal_status = search_df.iloc[i]["status"]
			if proposal_end is None or proposal_start is None:
				#print(proposal_id)
				pass
			else:
				proposal_start_dt = datetime.date(datetime.strptime(proposal_start, "%Y-%m-%d"))
				proposal_end_dt = datetime.date(datetime.strptime(proposal_end, "%Y-%m-%d"))
			start_date = datetime.date(datetime.strptime(str(start_date), "%Y-%m-%d"))
			end_date = datetime.date(datetime.strptime(str(end_date), "%Y-%m-%d"))
			if proposal_start is None or proposal_end is None:
				to_drop.append(i)
			elif start_date > proposal_end_dt:
				to_drop.append(i)
			elif proposal_start_dt > end_date:
				to_drop.append(i)

		#print(to_drop)
		search_df.drop(search_df.index[to_drop], inplace=True)
		#print(search_df)
		return search_df
	else:
		search_df = []
		return search_df

def item_generator(json_input, lookup_key):
    if isinstance(json_input, dict):
        for k, v in json_input.items():
            if k == lookup_key:
                yield v
            else:
                yield from item_generator(v, lookup_key)
    elif isinstance(json_input, list):
        for item in json_input:
            yield from item_generator(item, lookup_key)
            
            
     


def calc_playout(playout_df, df1):
	df1 = df1
	playout_df = playout_df
	print(playout_df)
	for ind in range(0, len(playout_df)):
		screen_id = playout_df.iloc[ind]["id"]
		breakdw = playout_df.iloc[ind]["breakdown"]
		break_df = pd.DataFrame.from_dict(breakdw)
		for i in range(0, len(break_df)):
			av_saturation = break_df.iloc[i]["average_saturation"]
			row = {"screen_id": screen_id,
					"average_saturation": av_saturation}
			df1.loc[len(df1)] = row
	return df1 

async def run_campaign_extractor(result):
	#result = result
	list_of_tasks = []
	for i in range(0, len(result)):
		list_of_tasks.append(campaign_ectractor(result[i]))
	await asyncio.sleep(2)
	print(result)
	print(*list_of_tasks)
	await asyncio.gather(*list_of_tasks)


async def campaign_ectractor(index):
	search_json = session.get("search_json", None)
	#print(search_json)
	search_df = pd.read_json(search_json)
	allocation_stats = session.get("allocation_stats", None)
	saved = session.get("saved", None)
	#print(search_df)
	start_date = session.get("start_date", None)
	headers = session.get("headers", None)
	env = session.get("env", None)
	preempt = session.get("preempt", None)
	if preempt != None:
		preempt = 1
	else:
		preempt = 0
	#print(preempt)
	#print(index)
	end_date = session.get("end_date", None)
	index = index
	if allocation_stats != None:
		allocation_stats = 1
	else:
		allocation_stats = 0
	csv_data = {
	"BS Direct": [],
    "proposal id": [],
    "proposal name": [],
     "PLI ID": [],
    "PLI Name": [],
	"Slot Duration": [],
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
    "Start time": [],
    "End date": [],
    "End time": [],
    "DoW mask": [],
	"Hold Expiry Date": [],
    "BSC ID": [],
    "Priority": [],
    "Is pre-empt": [],
    "Performance update": [],
    "Auto Rebalance": [],
    "Booking time": [],
    "Allocation St. Dev": [],
    "Allocation Av. Saturation": [],
	"In Risk": [],
	"Allocated plays": [],
	"Allocated impressions": [],
	"Forecast plays in %": [],
	"Forecast impressions in %": []
}
	#csv_df = pd.DataFrame(csv_data)

	if 1 == 1:
		df_sat = []
		df_sat = pd.DataFrame(df_sat)
		df_repetitions = []
		df_impressions = []

		df_repetitions = pd.DataFrame(df_repetitions)
		df_impressions = pd.DataFrame(df_impressions)

		proposal_id = search_df.iloc[index]["id"]
		proposal_name = search_df.iloc[index]["name"]
		proposal_hold_expiery_tm = search_df.iloc[index]["hold_expiry_tm"]
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
			pass
		elif start_date <= proposal_start_dt and end_date >= proposal_start_dt or proposal_status == 11 and start_date >= proposal_start_dt or proposal_status == 14 and start_date <= proposal_end_dt and end_date >= proposal_end_dt:
			pli_url = env+"api/v1/proposal/"+str(proposal_id)+"/proposal_items"
			pli = requests.request("POST", url=pli_url, headers=headers, data=[])
			if pli.status_code == 200:
				to_drop = []
				pli_df = pd.DataFrame.from_dict(pli.json()["data"])
				for i in range(0, len(pli_df)):
					pli_is_preempt_raw = pli_df.iloc[i]["is_preemptible"]
					#print(pli_is_preempt_raw)
					pli_status_id = pli_df.iloc[i]["status"]
					pli_end_dt = pli_df.iloc[i]["end_date"]
					pli_end =  datetime.date(datetime.strptime(pli_end_dt, "%Y-%m-%d"))
					pli_start_dt = pli_df.iloc[i]["start_date"]
					pli_start =  datetime.date(datetime.strptime(pli_start_dt, "%Y-%m-%d"))
					pli_std = "N/A"
					pli_mean = "N/A"
					sacrificed_flag = "N/A"
					if saved == None and pli_status_id == 1:
						to_drop.append(i)
					elif pli_status_id == 12:
						to_drop.append(i)
					elif pli_start > end_date:
						to_drop.append(i)
					elif pli_is_preempt_raw == True and preempt == 0:
						to_drop.append(i)
				#print(to_drop)
				pli_df.drop(pli_df.index[to_drop], inplace=True)
			else:
				flash("Broadsign Direct Search ERROR", category = "error") 

			if pli_df.empty:
				pass
			else:

				for index2 in range(0, len(pli_df)):
					mode_df = pd.DataFrame.from_dict(pli_df.iloc[index2]["mode"])
					tob_df = mode_df[mode_df["active"]!=False]
					pli_tob_values = tob_df.iloc[0]["values"]
					pli_type = tob_df.iloc[0]["type"]
					pli_boundary = "N/A"
					pli_id = pli_df.iloc[index2]["id"]
					pli_name = pli_df.iloc[index2]["name"]
					pli_slot_duration = pli_df.iloc[index2]["slot_duration"]
					pli_tob = pli_df.iloc[index2]["active_type"]
					pli_cr_tm = pli_df.iloc[index2]["creation_tm"]
					pli_act_imp = pli_df.iloc[index2]["actual_impressions"]
					if pli_act_imp != pli_act_imp:
						pli_act_imp = 0
					else:
						pass
					pli_act_rep = pli_df.iloc[index2]["actual_repetitions"]
					if pli_act_rep != pli_act_rep:
						pli_act_rep = 0
					else:
						pass
					pli_perf_update = pli_df.iloc[index2]["performance_update_tm"]
					pli_target = pli_df.iloc[index2]["target"]
					pli_status_id = pli_df.iloc[index2]["status"]
					pli_start_dt = pli_df.iloc[index2]["start_date"]
					pli_end_dt = pli_df.iloc[index2]["end_date"]
					pli_end =  datetime.date(datetime.strptime(pli_end_dt, "%Y-%m-%d"))
					pli_start = datetime.date(datetime.strptime(pli_start_dt, "%Y-%m-%d"))
					pli_start_tm = pli_df.iloc[index2]["start_time"]
					pli_end_tm = pli_df.iloc[index2]["end_time"]
					pli_dow = pli_df.iloc[index2]["dow_mask"]
					pli_bsc_id = pli_df.iloc[index2]["provider_id"]
					pli_std = "N/A"
					pli_mean = "N/A"
					sacrificed_flag = "N/A"
					pli_allocated_reps = "N/A"
					pli_allocated_imps = "N/A"
					predicted_imps = 100
					predicted_reps = 100
					predicted_impressions = "N/A"
					predicted_repetitions = "N/A"
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
						if pli_status_id == 11 and pli_perf_update != None or  pli_status_id == 14 and pli_perf_update != None:
							pli_perf_actual = (pli_df.iloc[index2]["performance"])["actual"]
							pli_perf_projected = (pli_df.iloc[index2]["performance"])["projected"]
                        
							if pli_perf_actual is None:
								pli_perf_actual = 0
							if pli_perf_projected is None:
								pli_perf_projected = 0
							if pli_perf_actual < 1 or pli_perf_projected < 1:
								pli_cp = None
								pli_perf_projected = "N/A"
							else:
								pli_cp = round((pli_perf_actual * 100) / pli_perf_projected, None)
								pli_cp = int(pli_cp)
								#pli_cp = f"{pli_cp}%"
						else:
							pli_cp = None
							pli_perf_projected = "N/A"

						if (pli_status_id == 9 and allocation_stats == 1) or (pli_status_id == 10 and allocation_stats == 1) or (pli_status_id == 11 and allocation_stats == 1):
							
							
							      
							page = 0
							df1 = {}
							df2 = {}
							df3 = {}
							df1 = pd.DataFrame(df1)
							df2 = pd.DataFrame(df2)
							df3 = pd.DataFrame(df3)
							df_impressions = df_impressions.drop(df_impressions.index, inplace=True)
							df_repetitions = df_repetitions.drop(df_repetitions.index, inplace=True)

							while 1 == 1:
								page += 1 
								df1 = df1.drop(df1.index, inplace=True)
								df2 = df2.drop(df2.index, inplace=True)
								df3 = df3.drop(df3.index, inplace=True)
								playout_url = env+"api/v1/proposal/proposal_item/"+str(pli_id)+"/playout?page="+str(page)
								#print(playout_url)
								playout = requests.request("GET", url = playout_url, headers=headers, data=[])
								if playout.status_code == 200:
								
									
									total_page = playout.json()["total_pages"]

									try:
										playout_temp_df = pd.DataFrame.from_dict(playout.json()["screens"])
									except NameError:
										pli_std = "N/A"
										pli_mean = "N/A"
									except pd.errors.EmptyDataError:
										pli_std = "N/A"
										pli_mean = "N/A"
									else:
										
										output = []
										for i in item_generator(playout.json()["screens"], "average_saturation"):
											ans = {"average_saturation": i}
											output.append(ans)
										df1 = pd.DataFrame.from_dict(output)

										output_reps = []
										for i in item_generator(playout.json()["screens"], "repetitions"):
											ans = {"repetitions": i}
											output_reps.append(ans)
										df2 = pd.DataFrame.from_dict(output_reps)

										output_imps = []
										for i in item_generator(playout.json()["screens"], "impressions"):
											ans = {"impressions": i}
											output_imps.append(ans)
										df3 = pd.DataFrame.from_dict(output_imps)

										df_sat = pd.concat([df_sat, df1], ignore_index=True, sort=False)

										df_repetitions = pd.concat([df_repetitions, df2], ignore_index=True, sort=False)

										df_impressions = pd.concat([df_impressions, df3], ignore_index=True, sort=False)

										#df1_s_m = df_sat.average_saturation.agg(['std','mean'])
										#df_alocated_reps = df_repetitions.repetitions.agg(["sum"])
										#df_alocated_imps = df_impressions.impressions.agg(["sum"])
										#pli_std = round(df1_s_m["std"],4)
										#pli_mean = round(df1_s_m["mean"],4)
										#pli_allocated_reps = round(df_alocated_reps["sum"],0)
										#pli_allocated_imps = round(df_alocated_imps["sum"],0)

										#print(f"just before break statment total {total_page} and curren {page}")
										#print(f"proposal id {proposal_id} reps {pli_allocated_reps} and imps {pli_allocated_imps}") 
								else:
									break
										

								if int(total_page) == int(page):
									break
									
										
							#print(df1)
							
							try:
								df_sat.loc[df_sat['average_saturation']== -1, 'average_saturation' ] =0
							except NameError:
								pli_std = "N/A"
								pli_mean = "N/A"
							except KeyError:
								pli_std = "N/A"
								pli_mean = "N/A"
							else:
								df_sat.loc[df_sat['average_saturation']== -1, 'average_saturation' ] =0
										
								df1_s_m = df_sat.average_saturation.agg(['std','mean'])
								df_alocated_reps = df_repetitions.repetitions.agg(["sum"])
								df_alocated_imps = df_impressions.impressions.agg(["sum"])
								pli_std = round(df1_s_m["std"],4)
								pli_mean = round(df1_s_m["mean"],4)
								pli_allocated_reps = round(df_alocated_reps["sum"],0)
								pli_allocated_imps = round(df_alocated_imps["sum"],0)
						
									
									
								#print(f"proposal id {proposal_id} reps {pli_allocated_reps} and imps {pli_allocated_imps}")
								#print(df_impressions, df_repetitions)

										

							
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
							pli_imp_boundary = pli_imp_boundary  * 100
							pli_imp_boundary  = f"{pli_imp_boundary}%"
                    
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
							pli_av_sov_l_boundary = pli_av_sov_l_boundary * 100
							pli_av_sov_l_boundary = f"{pli_av_sov_l_boundary}%"
                            
						try:
							pli_tob_values["average_sov_upper_boundary"]
						except NameError:
							pli_av_sov_u_boundary = "N/A"
						except KeyError:
							pli_av_sov_u_boundary = "N/A"
						else:
							pli_av_sov_u_boundary = pli_tob_values["average_sov_upper_boundary"]
							pli_av_sov_u_boundary = pli_av_sov_u_boundary * 100
							pli_av_sov_u_boundary = f"{pli_av_sov_u_boundary}%S"
                     
						try:
							pli_tob_values["average_sov"]
						except NameError:
							pli_av_sov = "N/A"
						except KeyError:
							pli_av_sov = "N/A"
						else:
							pli_av_sov = pli_tob_values["average_sov"]
						
						#Forecast reps
						if type(pli_expect_rep) == str or pli_expect_rep is None:
							pass
						elif type(pli_act_rep) == str or pli_act_rep is None:
							pass
						elif type(pli_allocated_reps) == str or pli_allocated_reps is None:
							pass
						elif pli_expect_rep > 0:
							print(f"Expect imp{pli_expect_imp}, Expected reps {pli_expect_rep}")
							predicted_reps = (pli_act_rep + pli_allocated_reps) / int(pli_expect_rep)
							predicted_reps = predicted_reps * 100
							predicted_reps = round(predicted_reps, 2)
							predicted_repetitions = f"{predicted_reps}%"
						else:
							pass

						# Forecast impressions
						if type(pli_expect_imp) == str or pli_expect_imp is None:
							pass
						elif type(pli_act_imp) == str or pli_act_imp is None:
							pass
						elif type(pli_allocated_imps) == str or pli_allocated_imps is None:
							pass
						elif pli_expect_imp > 0:
							
							predicted_imps = (pli_allocated_imps + pli_act_imp) / int(pli_expect_imp)
							predicted_imps = predicted_imps * 100
							predicted_imps = round(predicted_imps, 2)

							predicted_impressions = f"{predicted_imps}%"
						else:
							pass
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
						pli_cp = None
						pli_perf_projected = "N/A"
                    
					
					pli_auto_reb = pli_df.iloc[index2]["last_auto_rebalance_tm"]
					pli_no_of_screens = pli_df.iloc[index2]["screen_count"]
					pli_booking_tm = pli_df.iloc[index2]["booking_tm"]

					long = datetime.date(datetime.strptime("2023-06-15", "%Y-%m-%d")) - datetime.date(datetime.strptime("2023-05-01", "%Y-%m-%d"))
					#print(long)
					date_now = time.strftime("%Y-%m-%d", time.gmtime())
					delta = datetime.date(datetime.strptime(str(pli_end), "%Y-%m-%d")) - datetime.date(datetime.strptime(str(date_now), "%Y-%m-%d"))
					camp_lenght = datetime.date(datetime.strptime(str(pli_end), "%Y-%m-%d"))  - datetime.date(datetime.strptime(str(pli_start), "%Y-%m-%d")) 
					#print( long, delta)
					

					if pli_mean == 0:
						sacrificed_flag = "No allocated plays"
					elif camp_lenght > long and delta > long:
						#print(f"*******Skipped one {pli_id} and camp length {camp_lenght} delta is {delta} and the period is {long}. Start {pli_start} and end {pli_end}")
						pass
					elif pli_tob == "goal_impressions" and predicted_imps < 90:
						#print(f"**** {pli_id}camp length {camp_lenght} delta is {delta} and the period is {long}. Start {pli_start} and end {pli_end}")
						sacrificed_flag = "Delivery risk"

					elif pli_tob == "goal_repetitions" and predicted_reps < 90:
						sacrificed_flag = "Delivery risk"

					elif pli_tob == "sov" and predicted_reps < 90:
						#print(f"**** {pli_id}camp length {camp_lenght} delta is {delta} and the period is {long}. Start {pli_start} and end {pli_end}")
						sacrificed_flag = "Delivery risk"

					elif pli_tob == "average_sov" and predicted_reps < 90:
						sacrificed_flag = "Delivery risk"

					else:
						pass

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
						pli_status = "Held"
					elif pli_status_id == 1:
						pli_status = "Saved"
					else:
						pli_status = "Other "+str(pli_status_id)
					proposal_hyperlink = F'=HYPERLINK("{env}proposal_builder.html?id={proposal_id}", "{proposal_id}")'
					csv_row = {
	"BS Direct": proposal_hyperlink,
    "proposal id": proposal_id,
    "proposal name": proposal_name,
    "PLI ID": pli_id,
    "PLI Name": pli_name,
	"Slot Duration": pli_slot_duration,
    "TOB": pli_tob,
    "Sub Type": pli_tob_sub,
    "Number of screens": pli_no_of_screens,
    "Creation Time": pli_cr_tm,
    "Actual Imp": pli_act_imp,
    "Actual Rep": pli_act_rep,
    "Expected_impressions": pli_expect_imp,
    "Expected today": pli_perf_projected,
    "Campaign Performance %": pli_cp,
    "Expected_repetitions": pli_expect_rep,
     "Imp/Rep goal": pli_target,
    "SoV goal": pli_sov,
    "Saturation": pli_saturation,
    "Imp Boundary": pli_imp_boundary,
    "Av. SoV lower boundary":  pli_av_sov_l_boundary,
    "Av. SoV upper boundary": pli_av_sov_u_boundary,
    "Av. SoV": pli_av_sov,
    "PLI Status": pli_status,
    "Start date": pli_start_dt,
    "Start time": pli_start_tm,
    "End date": pli_end_dt,
    "End time": pli_end_tm,
    "DoW mask": pli_dow,
	"Hold Expiry Date": proposal_hold_expiery_tm,
    "BSC ID": pli_bsc_id,
    "Priority": pli_prio,
    "Is pre-empt": pli_is_preempt,
    "Performance update": pli_perf_update,
    "Auto Rebalance": pli_auto_reb,
    "Booking time": pli_booking_tm,
    "Allocation St. Dev": pli_std,
    "Allocation Av. Saturation": pli_mean,
	"In Risk": sacrificed_flag,
	"Allocated plays": pli_allocated_reps,
	"Allocated impressions": pli_allocated_imps,
	"Forecast plays in %": predicted_repetitions,
	"Forecast impressions in %": predicted_impressions
}

					if pli_status_id == 12:
						pass
					elif pli_status_id == 14 and start_date >= pli_end:
						pass
					elif pli_status_id != 12:
						session["temp_json"].append(csv_row)
						#csv_df.loc[len(csv_df)] = csv_row
						#print(csv_row)
				 
                    
                    
                    
		
	#return csv_df




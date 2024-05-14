import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import time
import io
from flask import flash, session
import asyncio

def availiblity_frequency(headers, env, date, duration, tob_value):
	search_url = f"{env}api/v1/screen/search"
	search_pl = json.dumps(
		{
    "$top": 10000,
    "$skip": 0,
    "$sort": [
        {
            "field": "selection",
            "dir": "desc",
            "selected_screens": [],
            "type": "cart"
        }
    ],
    "criteria": [],
    "not_criteria": [],
    "available_only": False,
    "deployed_only": False,
    "dow_mask": 127,
    "multiplier": 1,
    "end_date": str(date),
    "end_time": "23:59:59",
    "start_date": str(date),
    "start_time": "00:00:00",
    "inventory_type": "digital",
    "gender_age": [],
    "resolution": [],
    "orientation": [],
    "screen_format": [],
    "category_ids": [],
    "slot_duration": duration,
    "mode": [
        {
            "type": "ppl",
            "values": {
                "bs_saturation": tob_value,
                "saturation": tob_value
            },
            "active": True
        }
    ],
    "proposal_goal_id": None,
    "dynamic_screen_quantity": 1,
    "keywords": []
}
    )
	screen_search = requests.request("POST", url=search_url, headers=headers, data=search_pl, files=[])
	if screen_search.status_code == 200:
		screens_df = pd.DataFrame.from_dict(screen_search.json()["data"])
		
		
        #print(screens_df)
		return screens_df
	else:
		return None
	



def availibility_checker():
	start_date = session.get("start_date", None)
	headers = session.get("headers", None)
	env = session.get("env", None)
	end_date = session.get("end_date", None)
	duration = session.get("duration", None)
	type_of_buy = session.get("type_of_buy", None)
	tob_value = session.get("tob_value", None)
	print(f"{start_date}, {end_date}, {duration}, {env}, {tob_value}, {type_of_buy}")
	if type_of_buy == "frequency":
		result = []
		
		date = end_date
		while date >= start_date:
			df = availiblity_frequency(headers, env, date, duration, tob_value)
		
			#print(len(result))
			if len(result) < 1 and  date == start_date:
				df3 = df
				df = df.astype({"availability": "int"})
				
				df3.rename(columns={"id": "Screen Id", "orientation": "Orientation", "resolution": "Resolution", "name": "Name"}, inplace=True)
				df.rename(columns={"availability": f"{date}", "id": "Screen Id"}, inplace=True)
				df.drop(df.columns.difference([f"{date}", "Screen Id"]), 1, inplace=True)
				#print(df3)
				df3.drop(df3.columns.difference(["Screen Id", "Name", "Orientation",  "Resolution" ]), 1, inplace=True)
				#print(df3)
				result = pd.merge(df3, df, on='Screen Id')
			elif len(result) < 1:
				df = df.astype({"availability": "int"})
				df.rename(columns={"availability": f"{date}", "id": "Screen Id"}, inplace=True)
				df.drop(df.columns.difference([f"{date}", "Screen Id"]), 1, inplace=True)
				result = df
			elif date == start_date:
				df3 = df
				df = df.astype({"availability": "int"})
				
				df3.rename(columns={"id": "Screen Id", "orientation": "Orientation", "resolution": "Resolution", "name": "Name"}, inplace=True)
				df.rename(columns={"availability": f"{date}", "id": "Screen Id"}, inplace=True)
				
				df.drop(df.columns.difference([f"{date}", "Screen Id"]), 1, inplace=True)
				#print(df3)
				df3.drop(df3.columns.difference(["Screen Id", "Name", "Orientation",  "Resolution" ]), 1, inplace=True)
				df2 = result
				#print(df3)
				result = pd.merge(df, df2, on='Screen Id')
				df2 = result
				result = pd.merge(df3, df2, on='Screen Id')
			elif len(result) > 1:
				df = df.astype({"availability": "int"})
				df.rename(columns={"availability": f"{date}", "id": "Screen Id"}, inplace=True)
				df.drop(df.columns.difference([f"{date}", "Screen Id"]), 1, inplace=True)
				df2 = result
				
				result = pd.merge(df, df2, on='Screen Id')
				
				#print(result.columns)
			date -= timedelta(days=1)
				
        
	else:
		#result = "Else"
		result = []
	#name = result.pop("name")
	#result.insert(1, "Name", name)
	return result

	
	

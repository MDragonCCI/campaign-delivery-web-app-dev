import requests
import json
import pandas as pd
import os 

FRAME_SERVICE_TOKEN = os.getenv("FRAME_SERVICE_TOKEN")



def frame_service_feach(offset, limit):
    offset = offset
    limit = limit
    url = f"https://4hfvgze7m8.execute-api.eu-west-1.amazonaws.com/PROD/frames/v2?offset={offset}&bu=GB&limit={limit}&frame_type=Digital"
    print(url)

    payload = json.dumps({
    "products": [
        "SAINSBURYS LIVE IN STORE",
        "ASDA LIVE",
        "SOCIALITE",
        "SAINSBURYS LIVE",
        "ASDA LIVE NORTHERN IRELAND",
        "STATION LIVE",
        "CC DIGITAL MALLS",
        "MALLS XL"
    ]
    })
    headers = {
    'x-api-key': FRAME_SERVICE_TOKEN,
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        frame_service_data = response.json()
    else:
        frame_service_data = None
    
    return frame_service_data


def frame_service_df():
    offset = 0
    limit = 500
    total_rows_number = 1000
    frame_df = {}
    while total_rows_number > offset:

        data = frame_service_feach(offset=offset, limit=limit)
        offset += 500
        if data != None:
            total_rows_number = data["totalCount"]
            df = pd.DataFrame.from_dict(data["data"])
            #print(df)
            if len(frame_df) == 0:
                frame_df = df
                df = {}
            else:
                frame_df = pd.concat([frame_df, df], ignore_index=True, sort=False)

        else:
            pass
        #print(offset, total_rows_number)
    return frame_df

def frame_bsd_data():
    data = {
        "Screen Id":[],
        "Commercial ID": [],
        "District Code": [],
        "Product": [],
        "Panel ID": [],
        "Address": [],
        "Post Code": [],
        "TV Area": [],
        "Conurbation": [],
        "Latitude": [],
        "Longitude": [],
        "Size": []
    }
    frame_df = frame_service_df()
    for i in range(0, len(frame_df)):
        screen_id = frame_df.iloc[i]["externalSystemIdentifiers"]["broadsign"]["screenId"] #bsd screen id
        dist_code = frame_df.iloc[i]["location"]["districtNo"] # distric code
        #print(dist_code)
        
        if screen_id is None:
            pass
        #elif dist_code > 0:
        #    print(dist_code)
        #    dist_code = 0
        else:
            commercial_id = frame_df.iloc[i]["externalSystemIdentifiers"]["space"]["commercialFrameId"] # commercialFrameId
            product = frame_df.iloc[i]["commercialInfo"]["product"]["name"] #Product
            panel_id = frame_df.iloc[i]["externalSystemIdentifiers"]["oasis"]["panelId"] # Oasis ID
            address = frame_df.iloc[i]["location"]["address"] #Address of the panel
            post_code = frame_df.iloc[i]["location"]["postcode"] #Postcode
            tv_area = frame_df.iloc[i]["location"]["levels"]["level1"] # TV area
            conurbation = frame_df.iloc[i]["location"]["levels"]["level2"] # Conurbation
            lat = frame_df.iloc[i]["location"]["geoLocation"]["latitude"] # latitude
            long = frame_df.iloc[i]["location"]["geoLocation"]["longitude"] #longitude
            size= frame_df.iloc[i]["physicalCharacteristics"]["size"] # Size

            #print(screen_id)
            data["Screen Id"].append(int(screen_id))
            data["Commercial ID"].append(int(commercial_id))
            data["District Code"].append(int(dist_code))
            data["Product"].append(product)
            data["Panel ID"].append(panel_id)
            data["Address"].append(address)
            data["Post Code"].append(post_code)
            data["TV Area"].append(tv_area)
            data["Conurbation"].append(conurbation)
            data["Latitude"].append(lat)
            data["Longitude"].append(long)
            data["Size"].append(size)

            
       
    
    result = pd.DataFrame.from_dict(data)
    

    return result



    
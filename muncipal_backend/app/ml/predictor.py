# ml/predictor.py
import __main__

# STEP 1: define function FIRST
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()  # removes extra spaces
    return text

# STEP 2: inject into __main__
__main__.clean_text = clean_text

import os
import joblib
import random
from .encoder import encode_issue_type
import re
import os
from dotenv import load_dotenv
import httpx

load_dotenv()
OVERPASS_URL = os.getenv("OVERPASS_URL")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Now use BASE_DIR to find your models in the same folder
CATEGORY_MODEL_PATH = os.path.join(BASE_DIR, 'category_model.pkl')
PRIORITY_MODEL_PATH = os.path.join(BASE_DIR, 'priority_model.pkl')

# Load them
category_model = joblib.load(CATEGORY_MODEL_PATH)

priority_model = joblib.load(PRIORITY_MODEL_PATH)




async def geocode_address(location: str):
    url = os.getenv("OPEN_STREET_URL")

    params = {
        "q": location,
        "format": "json",
    }

    headers = {
        "User-Agent": "municipal-ml-system",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()

        try:
            res = response.json()
        except ValueError:
            return None, None

    if not res:
        return None, None

    lat = float(res[0]["lat"])
    lon = float(res[0]["lon"])

    return lat, lon


async def predict_complaint(data , citizen_count):

    issue_type_encoded = encode_issue_type(data.issue_type)
    lat , lon = await geocode_address(data.location)
    nearby = await get_nearby_places(lat, lon)

    # description_input = [data.issue_description]
    predicted_category = category_model.predict([data.issue_description])[0]


    desc = data.issue_description.lower()
    if any(w in desc for w in ['accident','dangerous','injured','flooding','fire','collapse']):
        severity = random.randint(8 , 10)

    elif any(w in desc for w in ['overflowing','broken','large','not working']):
        severity = random.randint(5 , 7)

    else: 
        severity = random.randint(1 , 4)

    loc = data.location.lower()
    hospital_count = nearby["hospital_count"]
    school_count = nearby["school_count"]

    if hospital_count > 0:
        area_imp = 10
    elif school_count > 0:
        area_imp = 9
    else:
        area_imp = random.randint(2, 5)

    features = [[
        severity,            # Position 0: severity_score
        area_imp,            # Position 1: area_importance
        citizen_count,       # Position 2: citizen_reports_count
        issue_type_encoded   # Position 3: issue_type
    ]]


    priority_level = priority_model.predict(features)[0]


    norm_count = (citizen_count / 50) * 10
    priority_score = round((0.4 * severity) + (0.3 * norm_count) + (0.3 * area_imp), 2)
    
    report_id = f"RPT-{random.randint(100000, 999999)}"

    return {
        "report_id": report_id,
        "issue_description": data.issue_description,
        "location": data.location,
        "issue_type": str(predicted_category),
        "priority_level": str(priority_level),
        "priority_score": priority_score,
        "severity_score": severity,
        "area_importance": area_imp,
        "citizen_reports_count": citizen_count,
        "latitude" : lat,
        "longitude" : lon,

        "nearby" : nearby
    }


def format_places(elements):
    places = []
    for el in elements:
        places.append({
            "name": el.get("tags", {}).get("name", "Unknown"),
            "lat": el["lat"],
            "lon": el["lon"],
            "type": el.get("tags", {}).get("amenity")
        })
    return places



async def get_nearby_places(lat: float, lon: float, radius: int = 500):
    if lat is None or lon is None:
        return {
            "hospitals": [],
            "schools": [],
            "hospital_count": 0,
            "school_count": 0,
        }

    query = f"""
    [out:json];
    (
      node["amenity"="hospital"](around:{radius},{lat},{lon});
      node["amenity"="school"](around:{radius},{lat},{lon});
    );
    out;
    """

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            OVERPASS_URL, 
            data=query,
            headers={
                "Content-Type": "text/plain",
                "User-Agent": "municipal-ml-system"
            }
            )
        response.raise_for_status()

        try:
            data = response.json()
        except ValueError:
            return {
                "hospitals": [],
                "schools": [],
                "hospital_count": 0,
                "school_count": 0,
            }

    hospitals = []
    schools = []

    for element in data.get("elements", []):
        tags = element.get("tags", {})
        if tags.get("amenity") == "hospital":
            hospitals.append(element)
        elif tags.get("amenity") == "school":
            schools.append(element)

    return {
        "hospitals": format_places(hospitals),
        "schools": format_places(schools),
        "hospital_count": len(hospitals),
        "school_count": len(schools)
    }

  
        
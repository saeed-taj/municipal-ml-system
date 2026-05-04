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






BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Now use BASE_DIR to find your models in the same folder
CATEGORY_MODEL_PATH = os.path.join(BASE_DIR, 'category_model.pkl')
PRIORITY_MODEL_PATH = os.path.join(BASE_DIR, 'priority_model.pkl')




# Load them
category_model = joblib.load(CATEGORY_MODEL_PATH)

priority_model = joblib.load(PRIORITY_MODEL_PATH)




def predict_complaint(data , citizen_count):

    issue_type_encoded = encode_issue_type(data.issue_type)

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

    if 'hospital' in loc:
        area_imp = 10
    elif 'school' in loc : 
        area_imp = 9
    elif 'highway' in loc or 'main' in loc:
        area_imp = 8
    elif 'commercial' in loc or 'st' in loc:
        area_imp = 7
    else:
        area_imp = random.randint(2 , 5)

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
        "citizen_reports_count": citizen_count
    }
        
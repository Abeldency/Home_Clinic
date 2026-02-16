# logic.py - AI + Rule-Based Physician Engine

import joblib
import pandas as pd
import numpy as np
import os

# ==================================================
# 🧠 AI MODEL LOADING (SAFE)
# ==================================================
MODEL_AVAILABLE = False

try:
    if (
        os.path.exists("medical_model.pkl")
        and os.path.exists("scaler.pkl")
        and os.path.exists("encoder.pkl")
    ):
        model = joblib.load("medical_model.pkl")
        scaler = joblib.load("scaler.pkl")
        encoder = joblib.load("encoder.pkl")
        MODEL_AVAILABLE = True
except Exception as e:
    MODEL_AVAILABLE = False


# ==================================================
# 📚 RULE-BASED DIAGNOSIS TREE
# ==================================================
DIAGNOSIS_TREE = {
    "Cough": {
        "Dry": {"Medicine": "Dextromethorphan (Suppressant)", "Dosage": "10ml every 6-8 hours", "Bin": 7},
        "Wet (with Phlegm)": {"Medicine": "Guaifenesin (Expectorant)", "Dosage": "1 tablet every 4 hours", "Bin": 5}
    },
    "Fever": {
        "Mild (37.5-38°C)": {"Medicine": "Paracetamol", "Dosage": "500mg every 6 hours", "Bin": 1},
        "High (>38.5°C)": {"Medicine": "Ibuprofen", "Dosage": "400mg with food", "Bin": 2}
    },
    "Pain": {
        "Headache": {"Medicine": "Paracetamol", "Dosage": "500mg every 6 hours", "Bin": 3},
        "Muscle": {"Medicine": "Ibuprofen", "Dosage": "400mg every 8 hours", "Bin": 4},
        "Joint": {"Medicine": "Diclofenac", "Dosage": "50mg every 12 hours", "Bin": 6}
    },
    "Cold/Flu": {
        "Sneezing": {"Medicine": "Antihistamine", "Dosage": "10mg daily", "Bin": 8},
        "Runny Nose": {"Medicine": "Pseudoephedrine", "Dosage": "30mg every 8 hours", "Bin": 9},
        "Sore Throat": {"Medicine": "Lozenges", "Dosage": "1 every 2 hours", "Bin": 10}
    },
    "Stomach Issues": {
        "Nausea": {"Medicine": "Ondansetron", "Dosage": "4mg every 8 hours", "Bin": 11},
        "Acidity": {"Medicine": "Omeprazole", "Dosage": "20mg daily before breakfast", "Bin": 12},
        "Diarrhea": {"Medicine": "Loperamide", "Dosage": "2mg after first loose stool", "Bin": 13}
    },
    "Allergies": {
        "Skin Rash": {"Medicine": "Hydrocortisone Cream", "Dosage": "Apply 2x daily", "Bin": 14},
        "Itching": {"Medicine": "Cetirizine", "Dosage": "10mg daily", "Bin": 15},
        "Swelling": {"Medicine": "Loratadine", "Dosage": "10mg daily", "Bin": 16}
    },
    "Infections": {
        "UTI": {"Medicine": "Nitrofurantoin", "Dosage": "100mg twice daily", "Bin": 17},
        "Ear Infection": {"Medicine": "Amoxicillin", "Dosage": "500mg every 8 hours", "Bin": 18},
        "Skin Infection": {"Medicine": "Clindamycin Cream", "Dosage": "Apply 2x daily", "Bin": 19}
    },
    "Eye Issues": {
        "Redness": {"Medicine": "Artificial Tears", "Dosage": "2 drops every 4 hours", "Bin": 20},
        "Itching": {"Medicine": "Antihistamine Eye Drops", "Dosage": "2 drops 3x daily", "Bin": 21},
        "Infection": {"Medicine": "Ofloxacin Eye Drops", "Dosage": "1 drop every 6 hours", "Bin": 22}
    }
}


# ==================================================
# 🚨 EMERGENCY DETECTION
# ==================================================
EMERGENCY_KEYWORDS = [
    "chest pain",
    "breathing difficulty",
    "unconscious",
    "seizure",
    "severe bleeding",
    "heart attack",
    "stroke"
]

def detect_emergency(text):
    text = text.lower()
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in text:
            return True, keyword
    return False, None


# ==================================================
# 💊 RULE-BASED DIAGNOSIS (USED BY APP)
# ==================================================
def get_diagnosis(main_symptom, sub_symptom):
    category = DIAGNOSIS_TREE.get(main_symptom)
    if not category:
        return {"Medicine": "N/A", "Dosage": "N/A", "Bin": 0}
    return category.get(sub_symptom, {"Medicine": "N/A", "Dosage": "N/A", "Bin": 0})


def get_sub_options(main_symptom):
    return list(DIAGNOSIS_TREE.get(main_symptom, {}).keys())


def get_all_main_symptoms():
    return list(DIAGNOSIS_TREE.keys())


# ==================================================
# 🤖 AI-BASED DIAGNOSIS (NEW – OPTIONAL)
# ==================================================
def get_ai_diagnosis(input_data):
    """
    input_data format:
    [Age, Gender, Temp, HR, Sys, SpO2, WBC, CRP, Hb]
    """

    if not MODEL_AVAILABLE:
        return "AI model not available"

    column_names = [
        "Age", "Gender", "Temp", "HR",
        "Sys", "SpO2", "WBC", "CRP", "Hb"
    ]

    df_input = pd.DataFrame([input_data], columns=column_names)

    scaled_data = scaler.transform(df_input)
    prediction_numeric = model.predict(scaled_data)
    prediction_text = encoder.inverse_transform(prediction_numeric)[0]

    return prediction_text

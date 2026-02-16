# app.py - Omni-Med Vault (Voice + Diagnosis Only)
from logic import get_diagnosis, get_sub_options, get_all_main_symptoms, get_ai_diagnosis, detect_emergency
import streamlit as st
import sqlite3
import uuid
import tempfile
import os
import base64
from datetime import date

from emergency import show_emergency
from streamlit_mic_recorder import mic_recorder
#from voice import recognize_audio

# Page Config
st.set_page_config(page_title="💊 Asquare Med's", page_icon="💊")

# Background Image
def set_background(image_path):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
set_background("background.jpeg")

st.title("💊 Asquare Med's")
st.subheader("Your AI-Powered Home Clinic")

# ---------------------------
# Database Setup
conn = sqlite3.connect("clinic.db", check_same_thread=False, timeout=10)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE,
    age INTEGER,
    gender TEXT,
    dob TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS prescriptions (
    id TEXT PRIMARY KEY,
    patient_id TEXT,
    symptom TEXT,
    sub_symptom TEXT,
    medicine TEXT,
    dosage TEXT,
    bin INTEGER
)
""")
conn.commit()

# ---------------------------
# Session State
if "patient" not in st.session_state:
    st.session_state.patient = None

if "speech_symptom" not in st.session_state:
    st.session_state.speech_symptom = None

# ---------------------------
# Patient Registration / Auto Load
if st.session_state.patient is None:
    st.write("### 🧍 Register Patient")

    name = st.text_input("Name")

    existing_patient = None
    if name.strip() != "":
        c.execute("SELECT id, dob, gender, age FROM patients WHERE name = ?", (name,))
        existing_patient = c.fetchone()

    if existing_patient:
        patient_id, dob, gender, age = existing_patient
        st.session_state.patient = {
            "id": patient_id,
            "name": name,
            "DOB": dob,
            "age": age,
            "gender": gender
        }
        st.success("Existing patient loaded successfully!")

    else:
        dob = st.date_input("Date of Birth", value=date(2000, 1, 1), max_value=date.today())
        age = (date.today() - dob).days // 365
        st.write(f"Age: {age} years")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])

        if st.button("Register Patient"):
            if name.strip() == "":
                st.error("Name cannot be empty!")
            else:
                patient_id = str(uuid.uuid4())
                st.session_state.patient = {
                    "id": patient_id,
                    "name": name,
                    "DOB": str(dob),
                    "age": age,
                    "gender": gender
                }

                c.execute(
                    "INSERT INTO patients (id, name, dob, age, gender) VALUES (?, ?, ?, ?, ?)",
                    (patient_id, name, str(dob), age, gender)
                )
                conn.commit()
                st.success(f"Patient {name} registered successfully!")

# ---------------------------
# Main Application
if st.session_state.patient is not None:
    st.write(f"### Welcome, **{st.session_state.patient['name']}** 👋")
    st.write(f"Age: **{st.session_state.patient['age']}**, Gender: **{st.session_state.patient['gender']}**")

    # ---------------------------
    # 🎙 Voice Input
    st.write("### 🎙 Speak Your Symptoms")
    audio = mic_recorder(
        start_prompt="🎤 Start Recording",
        stop_prompt="⏹ Stop Recording",
        just_once=True,
        use_container_width=True
    )

    detected_symptom = None
    if audio and "bytes" in audio:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio["bytes"])
            audio_path = tmp.name

        #spoken_text = recognize_audio(audio_path)
        #os.remove(audio_path)

        #if spoken_text:
            #st.write(f"🗣 You said: **{spoken_text}**")

            #is_emergency, keyword = detect_emergency(spoken_text)
            #if is_emergency:
                #st.error("🚨 EMERGENCY DETECTED!")
                #st.error(f"Issue: {keyword.upper()}")
                #show_emergency(c, conn, st.session_state.patient["id"])
                #st.stop()

            #speech_symptom_map = {
                #"cough": "Cough",
                #"fever": "Fever",
                #"headache": "Headache",
                #"pain": "Pain",
                #"cold": "Cough",
                #"temperature": "Fever",
                #"breath": "Breathing Difficulty",
            #}

            #for key, value in speech_symptom_map.items():
                #if key in spoken_text.lower():
                    #st.session_state.speech_symptom = value
                    #st.success(f"Detected symptom from speech: **{value}**")
                    #break

    # ---------------------------
    # Symptom Selection
    st.write("### 🩺 Select Symptoms")
    main_symptom = st.selectbox(
        "Main Symptom",
        get_all_main_symptoms(),
        index=get_all_main_symptoms().index(st.session_state.speech_symptom)
        if st.session_state.speech_symptom in get_all_main_symptoms() else 0
    )

    sub_symptom = st.selectbox("Sub Symptom", get_sub_options(main_symptom))

    # ---------------------------
    # Diagnosis
    st.write("### 💊 Diagnosis")
    if st.button("Diagnose & Dispense"):
        result = get_diagnosis(main_symptom, sub_symptom)

        st.success(f"Medicine: {result['Medicine']}")
        st.info(f"Dosage: {result['Dosage']}")
        st.warning(f"Dispensing from Bin {result['Bin']}")

        c.execute("""
        INSERT INTO prescriptions VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            st.session_state.patient["id"],
            main_symptom,
            sub_symptom,
            result["Medicine"],
            result["Dosage"],
            result["Bin"]
        ))
        conn.commit()
        st.success("Prescription saved successfully!")

# =========================
# 🤖 AI Diagnosis (Enhanced UI)
st.subheader("🤖 AI-Powered Diagnosis")
st.caption("Smart analysis based on patient details & vitals")

# --- Basic Info ---
gender_options = ["Male", "Female", "Other"]
gender_value = st.session_state.patient.get('gender', "Male") if st.session_state.patient else "Male"
age_value = st.session_state.patient.get('age', 0) if st.session_state.patient else 0

st.divider()

# --- Body Metrics ---
st.markdown("### 🧍 Body Metrics")
m1, m2 = st.columns(2)
with m1:
    weight = st.number_input("⚖️ Weight (kg)", 1.0, 300.0, 70.0)
with m2:
    height = st.number_input("📏 Height (cm)", 30.0, 250.0, 170.0)

bmi = round(weight / ((height / 100) ** 2), 1)
st.info(f"🧮 **Calculated BMI:** {bmi}")
# --- Physical Activity (moved under AI Age/Gender) with icons ---
activity_options = {
    "🏃 Daily": 4,
    "🚴 2-3 times/week": 3,
    "🚶 Weekly": 2,
    "🛌 Monthly": 1
}
physical_activity_label = st.selectbox("🏋️ Physical Activity Level", list(activity_options.keys()))
activity_num = activity_options[physical_activity_label]

st.divider()

# --- Vital Signs ---
st.markdown("### ❤️ Vital Signs")
v1, v2, v3 = st.columns(3)
with v1:
    temp_ai = st.number_input("🌡 Temperature (°C)", 35.0, 42.0, 37.0)
    hr_ai = st.number_input("💓 Heart Rate (BPM)", 40, 180, 70)
with v2:
    bp_sys_ai = st.number_input("🩸 Systolic BP", 80, 200, 120)
    spo2_ai = st.number_input("🫁 SpO₂ (%)", 70, 100, 98)
with v3:
    wbc_ai = st.number_input("🧪 WBC (10⁹/L)", 1.0, 50.0, 6.0)
    crp_ai = st.number_input("🔥 CRP (mg/dL)", 0.0, 50.0, 1.0)
    hb_ai = st.number_input("🩸 Hemoglobin (g/dL)", 5.0, 20.0, 14.0)

st.divider()

# --- AI Action ---
ai_result = None
if st.button("🧠 Generate AI Diagnosis"):
    with st.spinner("🔍 Analyzing patient data..."):
        gender_num = 0 if gender_value == "Male" else 1 if gender_value == "Female" else 2
        patient_data = [
            age_value, gender_num, temp_ai, hr_ai,
            bp_sys_ai, spo2_ai, wbc_ai, crp_ai, hb_ai
        ]
        ai_result = get_ai_diagnosis(patient_data)

    st.subheader("📌 AI Prediction")
    st.success(f"🧾 **Diagnosis:** {ai_result}")


if ai_result is not None:
    if ai_result in ["Sepsis", "Hypoxia"]:
        st.error("🚨 **Critical Risk Detected** — Immediate medical attention required!")
        st.progress(90)
    else:
        st.success("✅ **Low Risk** — Follow standard treatment protocols")
        st.progress(40)

with st.expander("💡 AI Health Tip"):
    st.write(
        "This AI result is an assistive insight. "
        "Always combine AI predictions with clinical judgment."
    )

# ---------------------------
if st.session_state.patient is not None:
    show_emergency(c, conn, st.session_state.patient["id"])

# app.py - Omni-Med Vault (Voice + Diagnosis Only)
from logic import get_diagnosis, get_sub_options, get_all_main_symptoms, get_ai_diagnosis, detect_emergency
import streamlit as st
import sqlite3
import uuid
import tempfile
import os
import base64
from datetime import date

from emergency import show_emergency
from streamlit_mic_recorder import mic_recorder
#from voice import recognize_audio

# Page Config
st.set_page_config(page_title="💊 Asquare Med's", page_icon="💊")

# Background Image
def set_background(image_path):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
set_background(r"C:\Users\HP\Downloads\WhatsApp Image 2026-01-29 at 6.12.39 PM.jpeg")

st.title("💊 Asquare Med's")
st.subheader("Your AI-Powered Home Clinic")

# ---------------------------
# Database Setup
conn = sqlite3.connect("clinic.db", check_same_thread=False, timeout=10)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE,
    age INTEGER,
    gender TEXT,
    dob TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS prescriptions (
    id TEXT PRIMARY KEY,
    patient_id TEXT,
    symptom TEXT,
    sub_symptom TEXT,
    medicine TEXT,
    dosage TEXT,
    bin INTEGER
)
""")
conn.commit()

# ---------------------------
# Session State
if "patient" not in st.session_state:
    st.session_state.patient = None

if "speech_symptom" not in st.session_state:
    st.session_state.speech_symptom = None

# ---------------------------
# Patient Registration / Auto Load
if st.session_state.patient is None:
    st.write("### 🧍 Register Patient")

    name = st.text_input("Name")

    existing_patient = None
    if name.strip() != "":
        c.execute("SELECT id, dob, gender, age FROM patients WHERE name = ?", (name,))
        existing_patient = c.fetchone()

    if existing_patient:
        patient_id, dob, gender, age = existing_patient
        st.session_state.patient = {
            "id": patient_id,
            "name": name,
            "DOB": dob,
            "age": age,
            "gender": gender
        }
        st.success("Existing patient loaded successfully!")

    else:
        dob = st.date_input("Date of Birth", value=date(2000, 1, 1), max_value=date.today())
        age = (date.today() - dob).days // 365
        st.write(f"Age: {age} years")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])

        if st.button("Register Patient"):
            if name.strip() == "":
                st.error("Name cannot be empty!")
            else:
                patient_id = str(uuid.uuid4())
                st.session_state.patient = {
                    "id": patient_id,
                    "name": name,
                    "DOB": str(dob),
                    "age": age,
                    "gender": gender
                }

                c.execute(
                    "INSERT INTO patients (id, name, dob, age, gender) VALUES (?, ?, ?, ?, ?)",
                    (patient_id, name, str(dob), age, gender)
                )
                conn.commit()
                st.success(f"Patient {name} registered successfully!")

# ---------------------------
# Main Application
if st.session_state.patient is not None:
    st.write(f"### Welcome, **{st.session_state.patient['name']}** 👋")
    st.write(f"Age: **{st.session_state.patient['age']}**, Gender: **{st.session_state.patient['gender']}**")

    # ---------------------------
    # 🎙 Voice Input
    st.write("### 🎙 Speak Your Symptoms")
    audio = mic_recorder(
        start_prompt="🎤 Start Recording",
        stop_prompt="⏹ Stop Recording",
        just_once=True,
        use_container_width=True
    )

    detected_symptom = None
    if audio and "bytes" in audio:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio["bytes"])
            audio_path = tmp.name

        spoken_text = recognize_audio(audio_path)
        os.remove(audio_path)

        if spoken_text:
            st.write(f"🗣 You said: **{spoken_text}**")

            is_emergency, keyword = detect_emergency(spoken_text)
            if is_emergency:
                st.error("🚨 EMERGENCY DETECTED!")
                st.error(f"Issue: {keyword.upper()}")
                show_emergency(c, conn, st.session_state.patient["id"])
                st.stop()

            speech_symptom_map = {
                "cough": "Cough",
                "fever": "Fever",
                "headache": "Headache",
                "pain": "Pain",
                "cold": "Cough",
                "temperature": "Fever",
                "breath": "Breathing Difficulty",
            }

            for key, value in speech_symptom_map.items():
                if key in spoken_text.lower():
                    st.session_state.speech_symptom = value
                    st.success(f"Detected symptom from speech: **{value}**")
                    break

    # ---------------------------
    # Symptom Selection
    st.write("### 🩺 Select Symptoms")
    main_symptom = st.selectbox(
        "Main Symptom",
        get_all_main_symptoms(),
        index=get_all_main_symptoms().index(st.session_state.speech_symptom)
        if st.session_state.speech_symptom in get_all_main_symptoms() else 0
    )

    sub_symptom = st.selectbox("Sub Symptom", get_sub_options(main_symptom))

    # ---------------------------
    # Diagnosis
    st.write("### 💊 Diagnosis")
    if st.button("Diagnose & Dispense"):
        result = get_diagnosis(main_symptom, sub_symptom)

        st.success(f"Medicine: {result['Medicine']}")
        st.info(f"Dosage: {result['Dosage']}")
        st.warning(f"Dispensing from Bin {result['Bin']}")

        c.execute("""
        INSERT INTO prescriptions VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            st.session_state.patient["id"],
            main_symptom,
            sub_symptom,
            result["Medicine"],
            result["Dosage"],
            result["Bin"]
        ))
        conn.commit()
        st.success("Prescription saved successfully!")

# =========================
# 🤖 AI Diagnosis (Enhanced UI)
st.subheader("🤖 AI-Powered Diagnosis")
st.caption("Smart analysis based on patient details & vitals")

# --- Basic Info ---
gender_options = ["Male", "Female", "Other"]
gender_value = st.session_state.patient.get('gender', "Male") if st.session_state.patient else "Male"
age_value = st.session_state.patient.get('age', 0) if st.session_state.patient else 0

st.divider()

# --- Body Metrics ---
st.markdown("### 🧍 Body Metrics")
m1, m2 = st.columns(2)
with m1:
    weight = st.number_input("⚖️ Weight (kg)", 1.0, 300.0, 70.0)
with m2:
    height = st.number_input("📏 Height (cm)", 30.0, 250.0, 170.0)

bmi = round(weight / ((height / 100) ** 2), 1)
st.info(f"🧮 **Calculated BMI:** {bmi}")
# --- Physical Activity (moved under AI Age/Gender) with icons ---
activity_options = {
    "🏃 Daily": 4,
    "🚴 2-3 times/week": 3,
    "🚶 Weekly": 2,
    "🛌 Monthly": 1
}
physical_activity_label = st.selectbox("🏋️ Physical Activity Level", list(activity_options.keys()))
activity_num = activity_options[physical_activity_label]

st.divider()

# --- Vital Signs ---
st.markdown("### ❤️ Vital Signs")
v1, v2, v3 = st.columns(3)
with v1:
    temp_ai = st.number_input("🌡 Temperature (°C)", 35.0, 42.0, 37.0)
    hr_ai = st.number_input("💓 Heart Rate (BPM)", 40, 180, 70)
with v2:
    bp_sys_ai = st.number_input("🩸 Systolic BP", 80, 200, 120)
    spo2_ai = st.number_input("🫁 SpO₂ (%)", 70, 100, 98)
with v3:
    wbc_ai = st.number_input("🧪 WBC (10⁹/L)", 1.0, 50.0, 6.0)
    crp_ai = st.number_input("🔥 CRP (mg/dL)", 0.0, 50.0, 1.0)
    hb_ai = st.number_input("🩸 Hemoglobin (g/dL)", 5.0, 20.0, 14.0)

st.divider()

# --- AI Action ---
ai_result = None
if st.button("🧠 Generate AI Diagnosis"):
    with st.spinner("🔍 Analyzing patient data..."):
        gender_num = 0 if gender_value == "Male" else 1 if gender_value == "Female" else 2
        patient_data = [
            age_value, gender_num, temp_ai, hr_ai,
            bp_sys_ai, spo2_ai, wbc_ai, crp_ai, hb_ai
        ]
        ai_result = get_ai_diagnosis(patient_data)

    st.subheader("📌 AI Prediction")
    st.success(f"🧾 **Diagnosis:** {ai_result}")


if ai_result is not None:
    if ai_result in ["Sepsis", "Hypoxia"]:
        st.error("🚨 **Critical Risk Detected** — Immediate medical attention required!")
        st.progress(90)
    else:
        st.success("✅ **Low Risk** — Follow standard treatment protocols")
        st.progress(40)

with st.expander("💡 AI Health Tip"):
    st.write(
        "This AI result is an assistive insight. "
        "Always combine AI predictions with clinical judgment."
    )

# ---------------------------
if st.session_state.patient is not None:
    show_emergency(c, conn, st.session_state.patient["id"])
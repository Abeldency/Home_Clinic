import streamlit as st
import uuid
from datetime import datetime

def show_emergency(c, conn, patient_id):
    # ---------------------------
    # Emergency Section
    # ---------------------------
    st.markdown("---")
    st.subheader("🚨 Emergency")

    st.write("Select the emergency reason and contact help immediately.")

    # 1️⃣ Emergency Reason Selection
    emergency_reason = st.selectbox(
        "Emergency Reason",
        [
            "Chest Pain",
            "Breathing Difficulty",
            "High Fever",
            "Unconscious",
            "Seizure",
            "Severe Injury",
            "Other"
        ]
    )

    if st.button("🚨 CALL EMERGENCY NOW"):
        doctor_number = "+91-8891208582"
        ambulance_number = "108 / 112"

        # 3️⃣ Emergency Timestamp
        emergency_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        st.error("🚨 EMERGENCY ACTIVATED")
        st.warning(f"🕒 Time: {emergency_time}")
        st.warning(f"🚑 Reason: {emergency_reason}")

        # 2️⃣ Show Numbers (Copy Friendly)
        st.markdown("### 📞 Emergency Contacts")

        st.write("**Doctor Number (Copy & Call):**")
        st.code(doctor_number)

        st.write("**Ambulance Number (Copy & Call):**")
        st.code(ambulance_number)

        st.info("""
        🏥 What to do now:
        • Stay calm  
        • Do not give medicine unless advised  
        • Keep patient lying down  
        • Call ambulance if condition worsens  
        """)

        # Save Emergency in Database
        c.execute("""
            INSERT INTO prescriptions
            (id, patient_id, symptom, sub_symptom, medicine, dosage, bin)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            patient_id,
            "Emergency",
            emergency_reason,
            "N/A",
            emergency_time,
            0
        ))
        conn.commit()

        st.success("✅ Emergency event saved successfully")
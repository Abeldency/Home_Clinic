import pandas as pd
import random

def generate_patient_data(num_records=5000):
    data = []
    # These match the categories we defined for your AI logic
    categories = ['Healthy', 'Fever', 'Bacterial_Infection', 'Viral_Infection', 
                  'Sepsis', 'Hypertension', 'Hypotension', 'Hypoxia', 'Anemia', 'Hypothermia']
    
    for _ in range(num_records):
        age = random.randint(18, 90)
        gender = random.choice([0, 1]) # 0: Female, 1: Male
        case = random.choice(categories)
        
        # Base healthy values
        temp, hr, sys, spo2, wbc, crp, hb = 36.8, 75, 115, 98, 7.0, 1.5, 14.0
        
        # Applying your logic table rules
        if case == 'Sepsis':
            temp = random.choice([35.5, 39.5])
            sys, hr, crp = random.randint(70, 89), random.randint(120, 140), round(random.uniform(100, 200), 1)
        elif case == 'Bacterial_Infection':
            temp, wbc, crp = round(random.uniform(38.5, 40.5), 1), round(random.uniform(15, 25), 1), round(random.uniform(50, 100), 1)
        elif case == 'Hypoxia':
            spo2, hr = random.randint(80, 88), random.randint(100, 120)
        # ... (The rest of your logic table cases)

        data.append([age, gender, temp, hr, sys, spo2, wbc, crp, hb, case])

    return pd.DataFrame(data, columns=['Age', 'Gender', 'Temp', 'HR', 'Sys', 'SpO2', 'WBC', 'CRP', 'Hb', 'Diagnosis'])

# This saves the file in the same folder as your APP.py
df = generate_patient_data(5000)
df.to_csv('advanced_patient_dataset.csv', index=False)
print("✅ Phase 1 Complete: 'advanced_patient_dataset.csv' has been created!")
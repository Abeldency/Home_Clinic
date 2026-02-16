import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib

# 1. Load the data generated in Phase 1
df = pd.read_csv('advanced_patient_dataset.csv')

# 2. Encoding (Phase 2): Convert text labels to numbers
le = LabelEncoder()
df['Diagnosis'] = le.fit_transform(df['Diagnosis'])

# 3. Separate Features (Vitals) from Label (Diagnosis)
X = df.drop('Diagnosis', axis=1)
y = df['Diagnosis']

# 4. Split: 80% for studying, 20% for testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. Scaling (Phase 2): Normalize numbers for the AI
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

# 6. Training (Phase 3): Build the Random Forest "Brain"
model = RandomForestClassifier(n_estimators=100, random_state=42)
print("Training the AI model... 🧠")
model.fit(X_train_scaled, y_train)

# 7. Save the files (The "Big Three")
joblib.dump(model, 'medical_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(le, 'encoder.pkl')

print("✅ Phase 3 Complete!")
print("Files generated: medical_model.pkl, scaler.pkl, encoder.pkl")
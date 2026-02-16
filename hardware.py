# hardware.py – Manual Vitals & Blood Test Input (Safe Ranges)

def get_vital_limits():
    return {
        "temperature": (35.0, 42.0),        # °C
        "heart_rate": (30, 200),            # BPM
        "bp_systolic": (70, 200),            # mmHg
        "bp_diastolic": (40, 130),           # mmHg
        "glucose": (50, 400),                # mg/dL
        "rbc": (3.5, 6.5),                   # million/µL
        "wbc": (3000, 20000),                # cells/µL
        "platelets": (50000, 800000),        # /µL
        "creatinine": (0.3, 6.0),            # mg/dL
        "bun": (5, 80),                      # mg/dL
        "sodium": (120, 160),                # mEq/L
        "potassium": (2.5, 6.5)              # mEq/L
    }


def classify(value, low, high):
    if value < low:
        return "Low"
    elif value > high:
        return "High"
    return "Normal"

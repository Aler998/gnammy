import os
import json
from datetime import datetime

FILE_PATH = "sensor_data.json"
FILE_PATH2 = "sensor_data2.json"
MAX_ENTRIES = 15

def is_half_hour():
    # return True
    return (datetime.now().minute == 0 or datetime.now().minute == 30) and datetime.now().second < 3

def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return []

def save_data(data, file_path):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
        
def update_file(temp, file_path):
    data = load_data(file_path)
    reading = {
        "timestamp": datetime.now().strftime("%H:%M"),
        "temperature": round(temp)
    }
    data.append(reading)
    data = data[-MAX_ENTRIES:]  # Tieni solo gli ultimi 15
    save_data(data, file_path)
    return data
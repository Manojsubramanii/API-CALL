from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import random
import string
import threading
import time
from pymongo import MongoClient
import os

app = FastAPI()

# ✅ CORS FIX (IMPORTANT for React frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔐 MongoDB Atlas Connection
MONGO_URI = "mongodb+srv://MANOJ:Manoj%402003@cluster0.m9rnn0j.mongodb.net/?appName=Cluster0"

client = MongoClient(MONGO_URI)

db = client["patient_db"]
collection = db["patient_records"]

MAX_RECORDS = 10000

sites = ["Site A", "Site B", "Site C", "Site D"]
statuses = ["Active", "In Transit", "Delayed", "Completed"]
risk_levels = ["Low", "Medium", "High"]
compliance_levels = ["Compliant", "Non-Compliant"]

def random_id(prefix):
    return prefix + ''.join(random.choices(string.digits, k=5))

def generate_record():
    return {
        "patient_id": random_id("PAT"),
        "cane_id": random_id("CAN"),
        "container_id": random_id("CON"),
        "tank_id": random_id("TNK"),
        "date": str(datetime.now().date()),
        "time": datetime.now().strftime("%H:%M:%S"),
        "site_name": random.choice(sites),
        "status": random.choice(statuses),
        "avg_lead_time": round(random.uniform(1.0, 72.0), 2),
        "risk_level": random.choice(risk_levels),
        "compliance": random.choice(compliance_levels),
        "created_at": datetime.utcnow()
    }

def auto_generate():
    while True:
        total = collection.count_documents({})
        if total >= MAX_RECORDS:
            print("Reached 10,000 records.")
            break

        records = []
        for _ in range(2):
            if collection.count_documents({}) < MAX_RECORDS:
                records.append(generate_record())

        if records:
            collection.insert_many(records)
            print("Inserted:", len(records))

        time.sleep(60)

# Start background generator thread
threading.Thread(target=auto_generate, daemon=True).start()

@app.get("/api/data")
def get_data():
    total = collection.count_documents({})
    data = list(collection.find({}, {"_id": 0}))
    return {
        "total_records": total,
        "data": data
    }
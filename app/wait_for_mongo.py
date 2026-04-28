import time
import os
import pymongo
from subprocess import call

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")

while True:
    try:
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        client.admin.command("ping")
        print("MongoDB is ready")
        break
    except Exception:
        print("Waiting for MongDB...")
        time.sleep(2)

print("Running database seeder...")
call(["python", "seed_data.py"])

print("Starting application...")
call(["python", "app.py"])

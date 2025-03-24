from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import os

# MongoDB connection string (use environment variable in production)
MONGO_URI = os.getenv("MONGO_URI")

# Create MongoDB client
client = MongoClient(MONGO_URI) 

# Create or access database
db = client["certification_platform"]

# Create collections
users_collection = db["users"]
invigilators_collection = db["invigilators"]
tasks_collection = db["tasks"]
submissions_collection = db["submissions"]
test_results_collection = db["test_results"]

# Create indexes for faster queries
users_collection.create_index("email", unique=True)
invigilators_collection.create_index("email", unique=True)
tasks_collection.create_index("email")
submissions_collection.create_index("email")
test_results_collection.create_index("email")

print("Connected to MongoDB database!")

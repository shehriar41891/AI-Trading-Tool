import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

MONGO_CONNECTION_URI = os.getenv('MONGO_CONNECTION_STRING')

print('The connection string is', MONGO_CONNECTION_URI)

def database_connection():
    """Establishes a connection to MongoDB and returns the database object."""
    client = MongoClient(MONGO_CONNECTION_URI, server_api=ServerApi('1'))
    try:
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        return client["stock_database"]  # Return the database object
    except Exception as e:
        print(f"Connection error: {e}")
        return None

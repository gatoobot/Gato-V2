from pymongo import MongoClient
from dotenv import load_dotenv
import os 

load_dotenv()

uri = os.getenv('URI')
client = MongoClient(uri)

db = client['discord_bot']
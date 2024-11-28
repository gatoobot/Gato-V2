import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin import credentials, db

if not firebase_admin._apps:
    cred = credentials.Certificate("client_secret.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()
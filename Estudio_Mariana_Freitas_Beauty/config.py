import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables
load_dotenv()

# Firebase initialization
cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS'))
firebase_admin.initialize_app(cred)
db = firestore.client()

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Flask configuration
class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev')
    SALON_NAME = "Mariana Freitas Beauty"
    SALON_ADDRESS = "Piedade de Cima, em frente à pracinha, Visconde do Rio Branco, MG"
    SALON_WHATSAPP = "+55 32 99994-9235"
    SALON_HOURS = "Segunda a sábado, das 08h00 às 20h30"
    LOW_STOCK_THRESHOLD = 5 
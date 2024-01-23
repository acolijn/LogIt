import os
import json

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SECRETS_PATH = os.path.join(BASE_DIR, 'secrets', 'secrets.json')

# Load secrets
with open(SECRETS_PATH, 'r') as f:
    secrets = json.load(f)

class Config:
    ENV = 'development'	
    DEBUG = True
    MONGO_URI = secrets.get('MONGO_URI')
    SECRET_KEY = secrets.get('SECRET_KEY') 
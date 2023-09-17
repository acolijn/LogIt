import secrets

class Config:
    MONGO_URI = 'mongodb+srv://acolijn:I_love_mongoDB123!@cluster0.srrelu1.mongodb.net/logit_db'
    SECRET_KEY = secrets.token_hex(16) 


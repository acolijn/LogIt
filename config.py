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
    
    # OpenID Connect Configuration
    OIDC_ENABLED = secrets.get('OIDC_ENABLED', False)
    OIDC_CLIENT_ID = secrets.get('OIDC_CLIENT_ID', '')
    OIDC_CLIENT_SECRET = secrets.get('OIDC_CLIENT_SECRET', '')
    OIDC_DISCOVERY_URL = secrets.get('OIDC_DISCOVERY_URL', '')
    OIDC_REDIRECT_URI = secrets.get('OIDC_REDIRECT_URI', 'http://localhost:5000/auth/callback')
    OIDC_SCOPES = secrets.get('OIDC_SCOPES', 'openid profile email')
    OIDC_ALLOWED_GROUPS = secrets.get('OIDC_ALLOWED_GROUPS', [])  # e.g., ['xenon']
    OIDC_GROUP_CLAIM = secrets.get('OIDC_GROUP_CLAIM', 'groups')  # Claim name containing groups
    
    # Default logbooks for new SSO users
    DEFAULT_LOGBOOKS = secrets.get('DEFAULT_LOGBOOKS', ['xams'])
 
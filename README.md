# LogIt
Logbook app

For [documentation](https://logit.readthedocs.io/)

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/acolijn/LogIt.git
cd LogIt
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements-clean.txt
```

### 4. Configure secrets
```bash
cp secrets/secrets.json.example secrets/secrets.json
# Edit secrets/secrets.json with your MongoDB URI and secret key
```

### 5. Run the application

**Development:**
```bash
python run.py
```

**Production (with Gunicorn):**
```bash
gunicorn -w 4 -b 0.0.0.0:5001 "app:create_app('config.Config')"
```

## Configuration

Edit `secrets/secrets.json`:
```json
{
    "MONGO_URI": "mongodb://your-mongo-host:27017/logit",
    "SECRET_KEY": "generate-a-secure-random-key"
}
```

## Requirements
- Python 3.9+
- MongoDB 4.0+ 
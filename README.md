# LogIt

A web-based electronic logbook application for research laboratories, designed to track experiments, equipment status, and operational notes with multi-user support and fine-grained access control.

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/mongodb-4.0+-green.svg)](https://www.mongodb.com/)
[![Documentation](https://img.shields.io/badge/docs-readthedocs-blue.svg)](https://logit.readthedocs.io/)

📚 **[Full Documentation on ReadTheDocs](https://logit.readthedocs.io/)**

## Features

- 📝 **Logbook Management**: Multiple logbooks, rich text entries, file attachments, search & filter
- 📊 **Slow Control Integration**: Real-time sensor monitoring with interactive Plotly graphs
- 🔐 **Authentication**: Local login + optional OpenID Connect SSO with group-based access
- 👥 **User Management**: Fine-grained logbook permissions, admin panel, activity tracking
- 🏷️ **Keyword System**: Hierarchical keywords for organizing and filtering entries
- 📅 **Multiple Views**: Timeline, calendar, and table views for entries

👉 **[See detailed feature list in documentation](https://logit.readthedocs.io/en/latest/features.html)**

## Quick Start

**For detailed installation instructions, see the [Installation Guide](https://logit.readthedocs.io/en/latest/installation.html).**

### Prerequisites
- Python 3.9+
- MongoDB 4.0+
- Linux/macOS/Windows

### Basic Installation

1. **Clone the repository**
```bash
git clone https://github.com/acolijn/LogIt.git
cd LogIt
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
``` & Application

5. **Configure application secrets**
```bash
cp secrets/secrets.json.example secrets/secrets.json
# Edit secrets/secrets.json with your configuration
```

Minimal `secrets/secrets.json` for local development:
```json
{
  "MONGO_URI": "mongodb://localhost:27017/logit_db",
  "SECRET_KEY": "your-secret-key-here-change-in-production",
  "OIDC_ENABLED": false
}
```

6. **Create initial admin user**
```bash
nano secrets/secrets.json  # Edit with your settings
```

5. **Create admin user and run**
```bash
python create_admin.py
python run.py
```

Access at **http://localhost:5000**

📖 **[See full installation guide for production deployment](https://logit.readthedocs.io/en/latest/installation.html)** SSO Configuration (Optional)

To enable OpenID Connect SSO with Nikhef:

```json
{
  "MONGO_URI": "mongodb://localhost:27017/logit_db",
  "SECRET_KEY": "your-secret-key",
  
  "OIDC_ENABLED": true,
  "OIDC_CLIENT_ID": "your-client-id",
  "OIDC_CLIENT_SECRET": "your-client-secret",
  "OIDC_DISCOVERY_URL": "https://sso.nikhef.nl/.well-known/openid-configuration",
  "OIDC_REDIRECT_URI": "https://your-domain.nl/auth/callback",
  "OIDC_SCOPES": "openid profile email",
  "OIDC_ALLOWED_GROUPS": ["xenon"],
  "OIDC_GROUP_CLAIM": "groups",
  
Basic configuration in `secrets/secrets.json`:

```json
{
  "MONGO_URI": "mongodb://localhost:27017/logit_db",
  "SECRET_KEY": "your-secret-key-change-in-production",
  "OIDC_ENABLED": false
}
```

📖 **[Complete configuration guide](https://logit.readthedocs.io/en/latest/configuration.html)** including SSO setup, MongoDB authentication, and production settings.- High voltage (PMTs, anode, cathode, gate)

### Entry Management

- **Add Entry**: Create new logbook entries with text and attachments
- **Edit Entry**: Click edit icon to modify entry text
- **Update Keywords**: Modify keywords on existing entries
- **Search**: Use search bar to filter by keywords or text
- **Calendar**: View entries organized by date
- **Timeline**: Chronological view of all entries

### Admin Tasks

- **User Management**: Create/modify local users, update SSO user permissions
- **Logbook Management**: Create logbooks, manage user access
- **Database Activity**: Monitor recent operations
- **Keyword Management**: Add/remove global keywords

## Project Structure

```
LogIt/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── models/               # Data models and forms
│   │   ├── User.py          # User authentication model
│   │   ├── LogBookForm.py   # Form definitions
│   │   └── Registration.py
│   ├── routes/               # URL route handlers
│   │   ├── auth.py          # Login, SSO, user management
│   │   ├── main.py          # Core logbook functionality
│   │   └── slow_control.py  # Plotting and monitoring
│   ├── static/               # CSS, JavaScript, uploads
**Login** → **Create Logbook** → **Add Entries** → **Monitor/Search**

📖 **[Complete usage guide](https://logit.readthedocs.io/en/latest/usage.html)** with detailed workflows and examples.
### Running Tests
```bash
# Run application in development mode
python run.py

# Check MongoDB connection
curl http://localhost:5000/test-mongo
```

### Adding New Features

1. Documentation

- 📖 **[ReadTheDocs](https://logit.readthedocs.io/)** - Complete documentation
- 🚀 **[Installation Guide](https://logit.readthedocs.io/en/latest/installation.html)**
- ⚙️ **[Configuration](https://logit.readthedocs.io/en/latest/configuration.html)**
- 📝 **[Usage Guide](https://logit.readthedocs.io/en/latest/usage.html)**
- 🔧 **[API Reference](https://logit.readthedocs.io/en/latest/api_reference.html)**
- [SSO Setup Guide](docs/SSO_SETUP.md)
- [MongoDB Authentication](MONGODB_AUTH_SETUP.md)Acknowledgments

Developed for the XENON Dark Matter Research Project at Nikhef. Troubleshooting

Common issues and solutions in the [Installation Guide](https://logit.readthedocs.io/en/latest/installation.html#troubleshooting).welcome! Fork, create a feature branch, and open a pull request.

## License

Developed for research use at Nikhef. Check with repository owner for licensing.
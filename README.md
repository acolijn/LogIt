# LogIt

A web-based electronic logbook application for research laboratories, designed to track experiments, equipment status, and operational notes with multi-user support and fine-grained access control.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)
![MongoDB](https://img.shields.io/badge/mongodb-4.0+-green.svg)

## Features

### 📝 Logbook Management
- **Multiple Logbooks**: Create and manage separate logbooks for different experiments or systems
- **Rich Text Entries**: Add detailed entries with timestamps, keywords, and formatted text
- **Image Attachments**: Upload and attach images, PDFs, and Excel files to entries
- **Entry Editing**: Update entry text and modify keywords after submission
- **Search & Filter**: Search entries by keyword, date range, or text content
- **Timeline View**: Visual chronological display of all entries
- **Calendar View**: Monthly calendar showing entry distribution

### 📊 Slow Control Integration
- **Real-time Monitoring**: Display live sensor data from slow control systems
- **Interactive Plots**: Plotly-based graphs with zoom, pan, and time range selection
- **Multiple Sensor Groups**: Temperature, pressure, pump parameters, and high voltage monitoring
- **Synchronized Views**: All plots zoom/pan together for easy comparison
- **Auto-refresh**: Periodic updates to show latest data
- **Historical Data**: Access up to 672 hours (28 days) of historical measurements
- **Custom Range Slider**: Select specific time ranges for detailed analysis

### 🔐 Authentication & Access Control
- **Dual Authentication**: Support for both local login and OpenID Connect SSO (Nikhef)
- **Group-Based Access**: Restrict SSO access to specific organizational groups
- **Logbook-Level Permissions**: Fine-grained control over which users can access each logbook
- **Admin Panel**: Manage users, logbooks, and permissions through web interface
- **Secure Sessions**: Flask-Login integration with secure session management

### 👥 User Management
- **Local Users**: Traditional username/password authentication
- **SSO Users**: Automatic provisioning via OpenID Connect
- **Role-Based Access**: Admin vs regular user privileges
- **Per-Logbook Permissions**: Grant/revoke access to specific logbooks for each user
- **Activity Tracking**: Monitor database operations and user actions

### 🏷️ Keyword System
- **Hierarchical Keywords**: Organize entries with structured keywords
- **Keyword Management**: Add, remove, and search by keywords
- **Bulk Operations**: Update keywords across multiple entries
- **Auto-filtering**: Click keywords to instantly filter entries

## Quick Start

### Prerequisites
- Python 3.9 or higher
- MongoDB 4.0 or higher
- Linux/macOS/Windows with bash

### Installation

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
```

4. **Configure MongoDB**

Option A: Use local MongoDB without authentication (development):
```bash
# Start MongoDB service
sudo systemctl start mongodb
```

Option B: Set up MongoDB with authentication (recommended):
```bash
# See MONGODB_AUTH_SETUP.md for detailed instructions
bash setup_mongodb_auth_v2.sh
```

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
python create_admin.py
# Follow prompts to create admin account
```

7. **Run the application**

**Development mode:**
```bash
python run.py
# Access at http://localhost:5000
```

**Production mode (systemd service):**
```bash
# Copy service files
sudo cp logit-gunicorn.service /etc/systemd/system/
sudo cp logit-mongodb.service /etc/systemd/system/

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable logit-mongodb.service logit-gunicorn.service
sudo systemctl start logit-mongodb.service logit-gunicorn.service

# Check status
sudo systemctl status logit-gunicorn.service
```

## Configuration

### Core Settings (`secrets/secrets.json`)

```json
{
  "MONGO_URI": "mongodb://user:pass@localhost:27017/logit_db?authSource=logit_db",
  "SECRET_KEY": "generate-a-secure-random-key",
  "OIDC_ENABLED": false
}
```

### SSO Configuration (Optional)

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
  
  "DEFAULT_LOGBOOKS": ["xams"]
}
```

See [SSO_SETUP.md](docs/SSO_SETUP.md) for detailed SSO configuration.

### Environment Variables

Application timezone (for slow control data):
```bash
export APP_TZ="Europe/Amsterdam"
```

## Usage

### First Time Setup

1. **Login as admin** using credentials created with `create_admin.py`

2. **Create a logbook** via Admin panel:
   - Go to `/admin`
   - Fill in "Create New Logbook" form
   - Add users who should have access

3. **Add entries**:
   - Select your logbook
   - Click "Add Entry"
   - Fill in text, add keywords, attach images
   - Submit

### Slow Control Monitoring

For XAMS experiment (or configure for your system):
1. Ensure slow control data is being written to MongoDB collection `slow_control_data`
2. Navigate to `/plot/` route (accessible from XAMS logbook)
3. Use interactive plots to monitor:
   - Temperature sensors (TT201-TT401, etc.)
   - Pressure sensors (PT101-PT201)
   - Pump parameters (flow, temperature, power)
   - High voltage (PMTs, anode, cathode, gate)

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
│   │   ├── styles.css
│   │   ├── js/
│   │   └── upload/          # User-uploaded files
│   └── templates/            # HTML templates
├── config.py                 # Application configuration
├── run.py                    # Development server
├── requirements.txt          # Python dependencies
├── secrets/
│   └── secrets.json         # Configuration (gitignored)
├── docs/                    # Documentation
└── *.service                # Systemd service files
```

## API Endpoints

### Authentication
- `GET/POST /login` - Login page (local or SSO)
- `GET /login/sso` - Initiate SSO flow
- `GET /auth/callback` - SSO callback handler
- `GET /logout` - Logout current user

### Logbook Operations
- `GET /add-entry` - Entry creation form
- `POST /add-entry` - Submit new entry
- `GET /entries` - List/search entries
- `POST /update_entry/<id>` - Update entry text
- `POST /update-entry-keywords/<id>` - Update entry keywords
- `GET /calendar` - Calendar view
- `GET /timeline` - Timeline view

### Slow Control
- `GET /plot/` - Slow control dashboard
- `GET /plot/data/` - JSON data for plot updates

### Admin
- `GET/POST /admin` - Admin panel
- `GET /get-user-logbooks/<id>` - Get user permissions
- `GET /dbactivity.html` - Database activity log

## Development

### Running Tests
```bash
# Run application in development mode
python run.py

# Check MongoDB connection
curl http://localhost:5000/test-mongo
```

### Adding New Features

1. **New routes**: Add to `app/routes/`
2. **New templates**: Add to `app/templates/`
3. **New models**: Add to `app/models/`
4. **Database changes**: Consider migration scripts

### Logging

Application logs (systemd service):
```bash
sudo journalctl -u logit-gunicorn.service -f
```

MongoDB logs:
```bash
sudo journalctl -u logit-mongodb.service -f
```

## Security Considerations

- 🔒 Keep `secrets/secrets.json` secure (already in `.gitignore`)
- 🔒 Use HTTPS in production (not included, use nginx/apache reverse proxy)
- 🔒 Enable MongoDB authentication (see `MONGODB_AUTH_SETUP.md`)
- 🔒 Use strong `SECRET_KEY` for session security
- 🔒 Regularly update dependencies: `pip install -U -r requirements.txt`
- 🔒 Keep admin passwords strong and secure
- 🔒 Review user permissions periodically

## Troubleshooting

### Application won't start
```bash
# Check if port is in use
sudo lsof -i :5000

# Check MongoDB is running
sudo systemctl status mongod

# Check logs
sudo journalctl -u logit-gunicorn.service -n 50
```

### Can't login
- Verify user exists: Check MongoDB `users` collection
- For SSO: Check `OIDC_ENABLED` is `true` in secrets.json
- For local: Verify password with `create_admin.py`

### Plots not updating
- Check slow control data exists: Query `slow_control_data` collection
- Verify timestamp format matches expectations
- Check browser console for JavaScript errors

### File upload fails
- Check `app/static/upload/` directory exists and is writable
- Verify file extension is allowed (see `ALLOWED_EXTENSIONS` in `main.py`)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Documentation

- [SSO Setup Guide](docs/SSO_SETUP.md) - Detailed OpenID Connect configuration
- [MongoDB Authentication](MONGODB_AUTH_SETUP.md) - Securing MongoDB
- [SSO Implementation](SSO_IMPLEMENTATION.md) - Technical SSO details

## License

This project is developed for research use. Please check with the repository owner for licensing information.

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation in `docs/`
- Review systemd logs for error messages

## Acknowledgments

Developed for the XENON Dark Matter Research Project at Nikhef. 
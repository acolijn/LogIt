# OpenID Connect SSO Setup Guide

## Overview
Your LogIt application now supports authentication via Nikhef SSO using OpenID Connect (OIDC). This guide explains how to configure and use the SSO integration.

## Features Implemented

### 1. Dual Authentication System
- **SSO Login**: Users can authenticate via Nikhef institutional login
- **Local Login**: Admin and legacy users can still use username/password
- Both login methods are available on the same login page

### 2. Group-Based Access Control
- Only members of specified groups (e.g., "xenon") can log in
- Configurable via `OIDC_ALLOWED_GROUPS` in secrets.json

### 3. Logbook-Level Permissions
- **Default Access**: New SSO users automatically get access to configured logbooks (default: "xams")
- **Custom Access**: Admins can grant/revoke access to additional logbooks per user
- **Admin Override**: Admin users have access to all logbooks

## Configuration Steps

### 1. Contact Your Security Expert
Provide them with the following information:

**Authentication Protocol**: OpenID Connect (OIDC)

**Required Information from Nikhef**:
- Client ID
- Client Secret  
- Discovery URL (usually: `https://sso.nikhef.nl/.well-known/openid-configuration`)
- Group claim name (ask what field contains group memberships)

**Information to Provide**:
- **Callback/Redirect URI**: 
  - Development: `http://localhost:5000/auth/callback`
  - Production: `https://your-domain.nl/auth/callback`
- **Required Scopes**: `openid profile email`
- **Required Claims**:
  - `sub` (subject - unique user ID)
  - `iss` (issuer)
  - `name` (display name)
  - `email` (user email)
  - Group membership claim (e.g., `groups`, `eduperson_entitlement`)

### 2. Update secrets.json
Copy the example configuration:
```bash
cp secrets/secrets.json.example secrets/secrets.json
```

Edit `secrets/secrets.json` with the information from Nikhef:

```json
{
  "MONGO_URI": "mongodb://localhost:27017/logit",
  "SECRET_KEY": "your-secret-key-here",
  
  "OIDC_ENABLED": true,
  "OIDC_CLIENT_ID": "logit-xams",
  "OIDC_CLIENT_SECRET": "secret-from-nikhef",
  "OIDC_DISCOVERY_URL": "https://sso.nikhef.nl/.well-known/openid-configuration",
  "OIDC_REDIRECT_URI": "https://logit-xams.nikhef.nl/auth/callback",
  "OIDC_SCOPES": "openid profile email",
  "OIDC_ALLOWED_GROUPS": ["xenon"],
  "OIDC_GROUP_CLAIM": "groups",
  
  "DEFAULT_LOGBOOKS": ["xams"]
}
```

**Configuration Options**:
- `OIDC_ENABLED`: Set to `true` to enable SSO login
- `OIDC_ALLOWED_GROUPS`: List of groups allowed to access (empty = allow all authenticated users)
- `OIDC_GROUP_CLAIM`: Name of the claim containing group memberships
- `DEFAULT_LOGBOOKS`: Logbooks new SSO users can access by default

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Restart the Application
```bash
# If using systemd service
sudo systemctl restart logit-gunicorn.service

# Or if running manually
python run.py
```

## Usage

### For End Users

#### SSO Login
1. Go to the login page
2. Select the logbook you want to access
3. Click "Login with Nikhef SSO"
4. Authenticate with your Nikhef credentials
5. You'll be redirected back and logged in

#### Local Login (Admin)
1. Select your logbook
2. Enter your username and password in the "Local Login" section
3. Click "Login"

### For Administrators

#### Managing User Logbook Access
1. Log in as admin (local account)
2. Go to Admin page
3. Use the "Manage User Logbook Permissions" section:
   - Select a user from the dropdown
   - Their current logbook access will be displayed
   - Hold Ctrl/Cmd to select multiple logbooks
   - Click "Update User Permissions"

#### Creating New Logbooks
When you create a new logbook, you need to explicitly grant access to SSO users:
1. Create the logbook via Admin page
2. Grant access to specific users via "Manage User Logbook Permissions"

#### User Management
- **SSO Users**: Created automatically on first login with default logbook access
- **Local Users**: Must be created manually via "Register New User" form
- Both user types can have their logbook permissions managed the same way

## Access Control Model

The system uses three levels of access control:

### 1. Institute Level (SSO)
- Enforced by group membership in Nikhef SSO
- Only members of allowed groups can authenticate
- Configured via `OIDC_ALLOWED_GROUPS`

### 2. Application Level
- All authenticated users (local or SSO) can access the application
- SSO users must pass group check

### 3. Logbook Level
- Fine-grained permissions per user per logbook
- New SSO users get default logbooks
- Admins can grant/revoke access via admin panel
- Admin users bypass this check (access all logbooks)

## Troubleshooting

### "SSO login failed" Error
- Check that `OIDC_ENABLED` is `true` in secrets.json
- Verify Client ID and Secret are correct
- Ensure Discovery URL is accessible
- Check application logs for detailed error messages

### "Access denied! You must be a member of..." Error
- User is not in the allowed groups
- Verify the user's group membership with Nikhef IT
- Check that `OIDC_GROUP_CLAIM` matches the claim name provided by Nikhef

### "You do not have access to any logbooks" Error
- User authenticated successfully but has no logbook permissions
- Admin needs to grant logbook access via Admin panel
- Check `DEFAULT_LOGBOOKS` configuration

### User Can't Access a Specific Logbook
- Check their permissions via Admin panel
- Update their `allowed_logbooks` as needed
- Verify the logbook name matches exactly

## Security Notes

1. **Keep secrets.json Secure**: Never commit it to git (it's in .gitignore)
2. **Use HTTPS in Production**: SSO requires secure connections
3. **Admin Account**: Keep a local admin account for emergency access
4. **Regular Audits**: Review user logbook permissions periodically

## Database Schema Changes

### User Model Updates
New fields added to user documents:
```javascript
{
  _id: ObjectId,
  username: String,
  email: String,
  password: String (null for SSO users),
  is_admin: Boolean,
  auth_method: "local" | "sso",  // NEW
  sso_id: String,                  // NEW - unique SSO identifier
  sso_name: String,                // NEW - display name from SSO
  allowed_logbooks: [String]       // NEW - list of logbook names
}
```

### Migration
Existing users will need the `allowed_logbooks` field added. This happens automatically:
- Local users: Get empty array, controlled via `logbooks.users` (existing system)
- SSO users: Get array populated on login

## Questions for Nikhef Security Expert

When you meet with your security contact, confirm:
1. ✅ What is the exact Discovery URL?
2. ✅ What claim name contains group memberships? (`groups`, `eduperson_entitlement`, etc.)
3. ✅ What is the exact group identifier for xenon? (e.g., "xenon", "urn:mace:nikhef.nl:group:xenon")
4. ✅ Do we need any additional scopes beyond `openid profile email`?
5. ✅ What should we use as our Client ID?
6. ✅ Do you support PKCE (Proof Key for Code Exchange)?

## Support

For issues:
1. Check application logs: `journalctl -u logit-gunicorn.service -f`
2. Verify secrets.json configuration
3. Test with `OIDC_ENABLED=false` to use local login
4. Contact Nikhef IT for SSO-specific issues

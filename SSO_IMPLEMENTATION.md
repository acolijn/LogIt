# SSO Implementation Summary

## What Was Implemented

Your LogIt application now supports **OpenID Connect (OIDC) Single Sign-On** with Nikhef institutional login, while maintaining local admin login.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Migration (One Time)
```bash
python migrate_sso.py
```

### 3. Configure SSO
Copy and edit the secrets file:
```bash
cp secrets/secrets.json.example secrets/secrets.json
# Edit secrets/secrets.json with your Nikhef SSO credentials
```

### 4. Test with SSO Disabled First
Make sure `OIDC_ENABLED: false` in secrets.json, then start the app:
```bash
python run.py
```

### 5. Enable SSO After Configuration
Set `OIDC_ENABLED: true` in secrets.json and restart.

## Key Files Changed

### New Files
- `docs/SSO_SETUP.md` - Complete setup and usage documentation
- `secrets/secrets.json.example` - Configuration template
- `migrate_sso.py` - Database migration script

### Modified Files
- `requirements.txt` - Added Authlib for OIDC
- `config.py` - Added OIDC configuration options
- `app/__init__.py` - Initialize OAuth
- `app/models/User.py` - Added SSO fields and logbook permissions
- `app/models/LogBookForm.py` - Added user permission management form
- `app/routes/auth.py` - Added SSO login routes and user management
- `app/routes/main.py` - Added logbook access control decorator
- `app/templates/login.html` - Added SSO login button
- `app/templates/admin.html` - Added user permission management UI

## What You Need from Nikhef IT

Ask your security expert for:
1. **Client ID** for your application
2. **Client Secret** 
3. **Discovery URL** (likely: `https://sso.nikhef.nl/.well-known/openid-configuration`)
4. **Group claim name** (field containing group memberships)
5. **Xenon group identifier** (exact string/URI for the xenon group)

Provide them with:
- **Callback URL**: `https://your-domain.nl/auth/callback`
- **Required scopes**: `openid profile email`
- **Required claims**: `sub`, `iss`, `name`, `email`, plus group claim

## Features

✅ **Dual Login**: SSO and local login coexist  
✅ **Group-Based Access**: Only xenon group members can login via SSO  
✅ **Logbook Permissions**: Granular control over which users access which logbooks  
✅ **Admin Panel**: Manage user logbook permissions  
✅ **Auto-Provisioning**: New SSO users created automatically with default access  
✅ **Backward Compatible**: Existing local users continue to work  

## Architecture

```
Login Flow (SSO):
1. User clicks "Login with Nikhef SSO"
2. Redirected to Nikhef login page
3. User authenticates with Nikhef credentials
4. Nikhef redirects back with authorization code
5. App exchanges code for user info
6. Check: Is user in allowed group? (e.g., xenon)
7. Find or create user in database
8. Check: Does user have access to selected logbook?
9. Log user in with session

Login Flow (Local):
1. User enters username/password
2. Verify credentials
3. Check if user is in logbook's users list
4. Log user in with session
```

## Access Control Levels

1. **Institute Level**: Group membership (SSO only)
2. **Application Level**: Authentication (SSO or local)
3. **Logbook Level**: Per-user permissions (both SSO and local)

## Testing Before Go-Live

1. **Test with OIDC disabled**: Verify local login still works
2. **Run migration**: Add new fields to existing users
3. **Configure SSO**: Add credentials from Nikhef
4. **Test SSO with test user**: Verify group check works
5. **Test logbook permissions**: Verify access control
6. **Test admin panel**: Verify user management
7. **Test local admin**: Verify admin can still login locally

## Rollback Plan

If SSO causes issues, you can instantly disable it:
1. Set `OIDC_ENABLED: false` in secrets.json
2. Restart the application
3. All users can use local login

The database changes are backward compatible - existing functionality is preserved.

## Next Steps

1. Read full documentation: `docs/SSO_SETUP.md`
2. Run migration script: `python migrate_sso.py`
3. Contact Nikhef IT with the required information
4. Configure secrets.json with provided credentials
5. Test thoroughly in development
6. Deploy to production

## Support

For questions or issues, check:
- Application logs: `journalctl -u logit-gunicorn.service -f`
- SSO setup guide: `docs/SSO_SETUP.md`
- Test with `OIDC_ENABLED=false` to isolate issues

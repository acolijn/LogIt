.. _configuration:

Configuration
=============

LogIt configuration is managed through ``secrets/secrets.json``.

Core Configuration
------------------

Basic Settings
~~~~~~~~~~~~~~

.. code-block:: json

    {
      "MONGO_URI": "mongodb://localhost:27017/logit_db",
      "SECRET_KEY": "your-secret-key-here",
      "OIDC_ENABLED": false
    }

Configuration Keys
~~~~~~~~~~~~~~~~~~

``MONGO_URI``
    MongoDB connection string. Format:
    
    - Without auth: ``mongodb://localhost:27017/logit_db``
    - With auth: ``mongodb://user:pass@localhost:27017/logit_db?authSource=logit_db``

``SECRET_KEY``
    Secret key for session encryption. Generate with:
    
    .. code-block:: python
    
        import secrets
        print(secrets.token_hex(32))

``OIDC_ENABLED``
    Enable/disable OpenID Connect SSO (``true`` or ``false``)

SSO Configuration (Optional)
-----------------------------

To enable institutional SSO with OpenID Connect:

Full SSO Configuration
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: json

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

SSO Configuration Keys
~~~~~~~~~~~~~~~~~~~~~~

``OIDC_CLIENT_ID``
    Client ID provided by your SSO provider

``OIDC_CLIENT_SECRET``
    Client secret provided by your SSO provider

``OIDC_DISCOVERY_URL``
    OpenID Connect discovery endpoint URL

``OIDC_REDIRECT_URI``
    Callback URL for SSO (must match provider configuration)
    
    - Development: ``http://localhost:5000/auth/callback``
    - Production: ``https://your-domain.nl/auth/callback``

``OIDC_SCOPES``
    Space-separated list of OAuth scopes (usually ``"openid profile email"``)

``OIDC_ALLOWED_GROUPS``
    Array of group names that are allowed to log in via SSO
    
    - Leave empty ``[]`` to allow all authenticated users
    - Example: ``["xenon", "researchers"]``

``OIDC_GROUP_CLAIM``
    Name of the claim containing group memberships in the ID token
    
    - Common values: ``"groups"``, ``"eduperson_entitlement"``

``DEFAULT_LOGBOOKS``
    Array of logbook names new SSO users can access by default
    
    - Example: ``["xams", "common"]``

For detailed SSO setup instructions, see ``docs/SSO_SETUP.md``.

MongoDB Configuration
---------------------

Without Authentication (Development)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: json

    {
      "MONGO_URI": "mongodb://localhost:27017/logit_db"
    }

With Authentication (Production)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: json

    {
      "MONGO_URI": "mongodb://logit_user:password@localhost:27017/logit_db?authSource=logit_db"
    }

See ``MONGODB_AUTH_SETUP.md`` for setting up MongoDB authentication.

Remote MongoDB
~~~~~~~~~~~~~~

To connect to a remote MongoDB instance:

.. code-block:: json

    {
      "MONGO_URI": "mongodb://user:pass@remote-host:27017/logit_db?authSource=logit_db"
    }

Ensure MongoDB is configured to accept remote connections and firewall rules allow access.

Environment Variables
---------------------

Application Timezone
~~~~~~~~~~~~~~~~~~~~

Set the timezone for slow control data timestamps:

.. code-block:: bash

    export APP_TZ="Europe/Amsterdam"

Add to systemd service file:

.. code-block:: ini

    [Service]
    Environment="APP_TZ=Europe/Amsterdam"

Or add to ``.bashrc`` / ``.profile`` for development.

Flask Environment
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    export FLASK_ENV=development  # or production
    export FLASK_APP=run.py

Slow Control Configuration
--------------------------

Slow control data should be written to the MongoDB collection ``slow_control_data`` with documents in this format:

.. code-block:: javascript

    {
      "timestamp": ISODate("2024-01-01T12:00:00Z"),
      "TT201": 25.3,
      "TT202": 24.8,
      "PT101": 1.013,
      // ... other sensor readings
    }

Customize sensor groups in ``app/routes/slow_control.py``:

.. code-block:: python

    temperature_sensors = ["TT201", "TT202", "TT203"]
    pressure_sensors = ["PT101", "PT102"]

Logbook Configuration
---------------------

Logbooks are created via the admin panel, but you can also create them directly in MongoDB:

.. code-block:: javascript

    db.logbooks.insertOne({
      "name": "xams",
      "users": []  // ObjectIds of users with access
    })

Security Best Practices
-----------------------

1. **Strong SECRET_KEY**: Use a long random string (64+ characters)
2. **HTTPS in production**: Use nginx/apache with SSL certificates
3. **MongoDB authentication**: Always enable in production
4. **Restrict MongoDB bind IP**: Only allow localhost or specific IPs
5. **File permissions**: Ensure ``secrets/secrets.json`` is not world-readable

.. code-block:: bash

    chmod 600 secrets/secrets.json

6. **Firewall**: Block MongoDB port (27017) from public access
7. **Regular updates**: Keep dependencies up to date

Configuration Examples
----------------------

Development Setup
~~~~~~~~~~~~~~~~~

.. code-block:: json

    {
      "MONGO_URI": "mongodb://localhost:27017/logit_db",
      "SECRET_KEY": "dev-key-change-in-production",
      "OIDC_ENABLED": false
    }

Production with Local Auth
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: json

    {
      "MONGO_URI": "mongodb://logit_user:SecurePass123@localhost:27017/logit_db?authSource=logit_db",
      "SECRET_KEY": "long-random-secret-key-generated-with-secrets-module",
      "OIDC_ENABLED": false
    }

Production with SSO
~~~~~~~~~~~~~~~~~~~

.. code-block:: json

    {
      "MONGO_URI": "mongodb://logit_user:SecurePass123@localhost:27017/logit_db?authSource=logit_db",
      "SECRET_KEY": "long-random-secret-key-generated-with-secrets-module",
      "OIDC_ENABLED": true,
      "OIDC_CLIENT_ID": "logit-production",
      "OIDC_CLIENT_SECRET": "client-secret-from-sso-provider",
      "OIDC_DISCOVERY_URL": "https://sso.institution.org/.well-known/openid-configuration",
      "OIDC_REDIRECT_URI": "https://logit.institution.org/auth/callback",
      "OIDC_SCOPES": "openid profile email",
      "OIDC_ALLOWED_GROUPS": ["researchers", "admin"],
      "OIDC_GROUP_CLAIM": "groups",
      "DEFAULT_LOGBOOKS": ["main", "equipment"]
    }

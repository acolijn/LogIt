.. _installation:

Installation
============

This guide covers installation and deployment of LogIt.

Prerequisites
-------------

* Python 3.9 or higher
* MongoDB 4.0 or higher
* Linux/macOS/Windows with bash
* Git

Quick Installation
------------------

1. Clone the Repository
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    git clone https://github.com/acolijn/LogIt.git
    cd LogIt

2. Create Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install Dependencies
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pip install -r requirements.txt

4. Configure MongoDB
~~~~~~~~~~~~~~~~~~~~

**Option A: Development (no authentication)**

.. code-block:: bash

    # Start MongoDB service
    sudo systemctl start mongodb

**Option B: Production (with authentication)**

.. code-block:: bash

    # Run the authentication setup script
    bash setup_mongodb_auth_v2.sh

See ``MONGODB_AUTH_SETUP.md`` for detailed instructions.

5. Configure Application
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    cp secrets/secrets.json.example secrets/secrets.json
    # Edit secrets/secrets.json with your configuration

Minimal configuration for development:

.. code-block:: json

    {
      "MONGO_URI": "mongodb://localhost:27017/logit_db",
      "SECRET_KEY": "your-secret-key-here-change-in-production",
      "OIDC_ENABLED": false
    }

6. Create Admin User
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    python create_admin.py

Follow the prompts to create your admin account.

7. Run the Application
~~~~~~~~~~~~~~~~~~~~~~

**Development mode:**

.. code-block:: bash

    python run.py

Access at http://localhost:5000

**Production mode** (see Production Deployment section)

Production Deployment
---------------------

Using Systemd Services
~~~~~~~~~~~~~~~~~~~~~~

1. Copy service files:

.. code-block:: bash

    sudo cp logit-gunicorn.service /etc/systemd/system/
    sudo cp logit-mongodb.service /etc/systemd/system/

2. Update service files with your paths and user

3. Enable and start services:

.. code-block:: bash

    sudo systemctl daemon-reload
    sudo systemctl enable logit-mongodb.service logit-gunicorn.service
    sudo systemctl start logit-mongodb.service logit-gunicorn.service

4. Check status:

.. code-block:: bash

    sudo systemctl status logit-gunicorn.service
    sudo systemctl status logit-mongodb.service

View logs:

.. code-block:: bash

    sudo journalctl -u logit-gunicorn.service -f

Using Reverse Proxy (Nginx)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example Nginx configuration:

.. code-block:: nginx

    server {
        listen 80;
        server_name your-domain.com;

        location / {
            proxy_pass http://127.0.0.1:5001;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /static {
            alias /path/to/LogIt/app/static;
        }
    }

For HTTPS, use certbot to obtain SSL certificates.

Environment Variables
---------------------

Set application timezone for slow control data:

.. code-block:: bash

    export APP_TZ="Europe/Amsterdam"

Add to your systemd service file or shell profile.

Troubleshooting
---------------

Application Won't Start
~~~~~~~~~~~~~~~~~~~~~~~

Check if port is in use:

.. code-block:: bash

    sudo lsof -i :5000

Check MongoDB is running:

.. code-block:: bash

    sudo systemctl status mongod

Check logs:

.. code-block:: bash

    sudo journalctl -u logit-gunicorn.service -n 50

MongoDB Connection Issues
~~~~~~~~~~~~~~~~~~~~~~~~~

Verify MongoDB is accessible:

.. code-block:: bash

    mongosh "mongodb://localhost:27017/logit_db"

Check authentication settings in ``secrets/secrets.json``.

Permission Errors
~~~~~~~~~~~~~~~~~

Ensure upload directory is writable:

.. code-block:: bash

    chmod 755 app/static/upload
    chown -R your-user:your-group app/static/upload

Next Steps
----------

* :doc:`configuration` - Configure SSO, logbooks, and settings
* :doc:`usage` - Learn how to use LogIt

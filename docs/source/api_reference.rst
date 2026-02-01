API Reference
=============

This section documents the main modules and functions in LogIt.

Routes Module
-------------

Authentication Routes (auth.py)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Handles user authentication, login/logout, and SSO integration.

.. automodule:: app.routes.auth
   :members:
   :undoc-members:
   :show-inheritance:

Main Routes (main.py)
~~~~~~~~~~~~~~~~~~~~~

Core logbook functionality including entries, keywords, and file management.

.. automodule:: app.routes.main
   :members:
   :undoc-members:
   :show-inheritance:

Slow Control Routes (slow_control.py)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Real-time sensor monitoring and plotting functionality.

.. automodule:: app.routes.slow_control
   :members:
   :undoc-members:
   :show-inheritance:

Models Module
-------------

User Model
~~~~~~~~~~

User authentication and authorization model.

.. automodule:: app.models.User
   :members:
   :undoc-members:
   :show-inheritance:

LogBook Forms
~~~~~~~~~~~~~

Form definitions and validation.

.. automodule:: app.models.LogBookForm
   :members:
   :undoc-members:
   :show-inheritance:

Configuration
-------------

Application configuration and settings.

.. automodule:: config
   :members:
   :undoc-members:
   :show-inheritance:   

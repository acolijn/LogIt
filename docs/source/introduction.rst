Introduction
============

LogIt is a web-based electronic logbook application designed for research laboratories, 
particularly for high-energy physics experiments. It provides a centralized platform 
for documenting experiments, monitoring equipment, and tracking operational notes.

Key Features
------------

* **Multi-logbook support**: Manage separate logbooks for different experiments
* **Rich entry system**: Text entries with keywords, timestamps, and file attachments
* **Slow control integration**: Real-time monitoring of sensor data with interactive plots
* **Access control**: Fine-grained permissions per user per logbook
* **SSO support**: Optional OpenID Connect integration for institutional authentication
* **Search and filtering**: Find entries by keywords, date range, or text content
* **Calendar and timeline views**: Visualize entries chronologically

Architecture
------------

LogIt is built with:

* **Backend**: Flask (Python web framework)
* **Database**: MongoDB (document store)
* **Frontend**: Bootstrap + Plotly for interactive visualizations
* **Authentication**: Flask-Login with optional OpenID Connect
* **Deployment**: Gunicorn + systemd for production

Use Cases
---------

* **Experiment logging**: Document daily operations, observations, and incidents
* **Equipment monitoring**: Track sensor readings, temperatures, pressures, voltages
* **Shift logs**: Record shift activities and handover notes
* **Troubleshooting**: Maintain history of issues and resolutions
* **Collaboration**: Share information across research teams

Target Audience
---------------

LogIt is designed for:

* Research laboratories with multiple experiments or systems
* Teams requiring centralized documentation
* Projects needing equipment monitoring alongside manual logging
* Facilities requiring access control and audit trails

Next Steps
----------

* :doc:`features` - Detailed feature descriptions
* :doc:`installation` - How to install and deploy LogIt
* :doc:`configuration` - Configuration options
* :doc:`usage` - User guide and workflows


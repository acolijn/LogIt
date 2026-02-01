Features
========

LogIt provides comprehensive features for laboratory documentation and monitoring.

Logbook Management
------------------

Multiple Logbooks
~~~~~~~~~~~~~~~~~
Create and manage separate logbooks for different experiments, systems, or teams. Each logbook maintains its own set of entries, keywords, and user permissions.

Rich Text Entries
~~~~~~~~~~~~~~~~~
Add detailed entries with:

* Timestamps (automatically recorded)
* Formatted text content
* Keywords for categorization
* Author attribution
* Edit history

File Attachments
~~~~~~~~~~~~~~~~
Attach various file types to entries:

* Images (PNG, JPG, GIF, BMP)
* Documents (PDF)
* Spreadsheets (XLS, XLSX)

Entry Management
~~~~~~~~~~~~~~~~

* **Add entries**: Create new logbook entries with text and attachments
* **Edit entries**: Modify entry text after submission
* **Update keywords**: Change keywords on existing entries
* **Delete capability**: Remove entries if needed (admin)

Search and Filtering
--------------------

Keyword Search
~~~~~~~~~~~~~~
Filter entries by selecting one or more keywords. Keywords are hierarchical and can be organized by category.

Text Search
~~~~~~~~~~~
Full-text search across all entry content to find specific information.

Date Range Filtering
~~~~~~~~~~~~~~~~~~~~
Select specific date ranges to view entries from a particular time period.

Views
-----

Timeline View
~~~~~~~~~~~~~
Chronological display of all entries, showing the flow of activities over time.

Calendar View
~~~~~~~~~~~~~
Monthly calendar visualization showing entry distribution and density.

Table View
~~~~~~~~~~
Paginated table of entries with sorting and filtering options.

Slow Control Integration
------------------------

Real-time Monitoring
~~~~~~~~~~~~~~~~~~~~
Display live sensor data from slow control systems stored in MongoDB. Supports various sensor types:

* Temperature sensors
* Pressure sensors
* Flow meters
* High voltage monitors
* Custom sensors

Interactive Plots
~~~~~~~~~~~~~~~~~
Plotly-based interactive graphs with:

* Zoom and pan controls
* Time range selection
* Synchronized views (all plots zoom together)
* Range slider for historical data navigation
* Auto-refresh for live updates

Plot Features
~~~~~~~~~~~~~

* **Multiple sensor groups**: Organize sensors into logical groups
* **Historical data**: Access up to 28 days of measurements
* **Custom time ranges**: Select specific periods for detailed analysis
* **Download plots**: Save as PNG images with timestamps
* **Responsive design**: Works on desktop and tablet devices

Authentication & Access Control
--------------------------------

Dual Authentication
~~~~~~~~~~~~~~~~~~~
Support for both:

* **Local login**: Traditional username/password
* **SSO login**: OpenID Connect integration (optional)

User Types
~~~~~~~~~~

* **Admin users**: Full access to all logbooks and admin panel
* **Regular users**: Access only to permitted logbooks
* **SSO users**: Auto-provisioned from institutional authentication

Access Control Levels
~~~~~~~~~~~~~~~~~~~~~

1. **Institute level**: Group membership (for SSO users)
2. **Application level**: User authentication
3. **Logbook level**: Per-user per-logbook permissions

Admin Panel
~~~~~~~~~~~

Administrators can:

* Create and manage logbooks
* Create local user accounts
* Manage logbook permissions for all users
* View database activity logs
* Manage global keywords

Keyword System
--------------

Hierarchical Keywords
~~~~~~~~~~~~~~~~~~~~~
Organize entries with structured, hierarchical keywords that can represent:

* Systems/subsystems
* Event types
* Priorities
* Status indicators

Keyword Management
~~~~~~~~~~~~~~~~~~

* Add new keywords via admin panel
* Remove unused keywords
* Bulk keyword updates
* Auto-completion when adding entries

Multi-select Filtering
~~~~~~~~~~~~~~~~~~~~~~
Click multiple keywords to filter entries across categories simultaneously.

Database Activity Monitoring
-----------------------------

Activity Log
~~~~~~~~~~~~
View recent database operations:

* Collection modifications
* User actions
* Timestamps
* Operation types

This helps track system usage and troubleshoot issues.

API and Integration
-------------------

RESTful Endpoints
~~~~~~~~~~~~~~~~~
LogIt provides JSON API endpoints for:

* Entry retrieval and creation
* Keyword management
* Slow control data updates
* User authentication

External Integration
~~~~~~~~~~~~~~~~~~~~
Can be integrated with:

* Slow control systems (via MongoDB)
* Institutional SSO providers
* Monitoring dashboards
* Automation scripts

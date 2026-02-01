.. _usage:

Usage Guide
===========

This guide explains how to use LogIt for daily operations.

First Time Setup
----------------

1. Login as Admin
~~~~~~~~~~~~~~~~~

Use the credentials you created with ``create_admin.py``:

- Navigate to http://your-server:5000
- Select your logbook from dropdown (or create one first)
- Enter admin username and password
- Click "Login"

2. Create a Logbook
~~~~~~~~~~~~~~~~~~~

From the Admin panel:

1. Go to ``/admin`` (click Admin link in navigation)
2. Find "Create New Logbook" section
3. Enter logbook name (e.g., "xams", "experiment1")
4. Optionally add users who should have access
5. Click "Create Logbook"

3. Add Users
~~~~~~~~~~~~

**Local users:**

1. In Admin panel, find "Register New User" section
2. Enter username, full name, email
3. Set password
4. Check "Admin" box if needed
5. Select logbooks this user can access
6. Click "Register User"

**SSO users:**

- SSO users are created automatically on first login
- Configure their logbook access via "Manage User Logbook Permissions"

Adding Entries
--------------

Create a New Entry
~~~~~~~~~~~~~~~~~~

1. Click "Add Entry" in navigation
2. Fill in the text box with your entry content
3. (Optional) Add keywords:
   
   - Click "Select Keywords" button
   - Choose from existing keywords
   - Or add new keywords in Admin panel first

4. (Optional) Attach files:
   
   - Click "Choose Files" button
   - Select images, PDFs, or Excel files
   - Multiple files can be attached

5. Click "Add Entry"

The entry will be saved with:

- Current timestamp
- Your username as author
- Selected keywords
- Attached files

Entry Best Practices
~~~~~~~~~~~~~~~~~~~~

- Be descriptive but concise
- Use keywords consistently for easier searching
- Attach relevant images or data files
- Document unusual observations or issues
- Include context for future reference

Editing Entries
---------------

Edit Entry Text
~~~~~~~~~~~~~~~

1. Find the entry in the entries list
2. Click the edit icon (pencil) next to the entry
3. Modify the text in the modal dialog
4. Click "Save Changes"

Update Keywords
~~~~~~~~~~~~~~~

1. Click the keywords icon for an entry
2. Select/deselect keywords
3. Click "Update Keywords"

Note: Only the entry author or admin can edit entries.

Searching and Filtering
------------------------

Search by Keyword
~~~~~~~~~~~~~~~~~

1. Go to "Entries" page
2. Click on any keyword to filter entries
3. Click multiple keywords to combine filters
4. Click "Clear Filters" to reset

Search by Text
~~~~~~~~~~~~~~

1. Use the search box at top of Entries page
2. Enter any text to search within entry content
3. Results update automatically

Date Range Filtering
~~~~~~~~~~~~~~~~~~~~

1. Use the date range selector (if available)
2. Select start and end dates
3. Click "Apply" to filter

View Options
~~~~~~~~~~~~

- **Table view**: Paginated list with sorting
- **Timeline view**: Chronological display
- **Calendar view**: Monthly calendar with entry markers

Slow Control Monitoring
-----------------------

Accessing Plots
~~~~~~~~~~~~~~~

For experiments with slow control integration:

1. Select the appropriate logbook (e.g., "xams")
2. Navigate to ``/plot/`` route (link in navigation)
3. View interactive plots of sensor data

Using Interactive Plots
~~~~~~~~~~~~~~~~~~~~~~~~

**Zoom and Pan:**

- Click and drag to zoom into a time range
- Double-click to reset zoom
- Use mouse wheel to zoom in/out

**Time Range Selection:**

- Use range slider at bottom of first plot
- Drag handles to select time range
- All plots will update simultaneously

**Synchronized Views:**

- Zooming one plot zooms all plots
- Helps correlate events across sensors

**Download Plots:**

- Click camera icon in plot toolbar
- Select format (PNG recommended)
- File saves with timestamp in filename

**Auto-Refresh:**

- Plots update automatically every 60 seconds
- Shows latest data if you're at the right edge of time range

Sensor Groups
~~~~~~~~~~~~~

Default sensor groups (configurable):

- **Temperature**: Cryostat temperatures (TT201-TT401, etc.)
- **Pressure**: System pressures (PT101-PT201)
- **Pump**: Pump temperature, flow, power
- **High Voltage**: PMT voltages and currents

Keywords Management
-------------------

Viewing Keywords
~~~~~~~~~~~~~~~~

Click "Keywords" in navigation to see all available keywords.

Adding Keywords (Admin)
~~~~~~~~~~~~~~~~~~~~~~~

1. Go to Admin panel
2. Find "Keyword Management" section
3. Enter new keyword name
4. Click "Add Keyword"

Removing Keywords (Admin)
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Select keyword from list
2. Click "Remove Keyword"
3. Confirm deletion

Note: Removing a keyword doesn't delete entries, just removes the keyword tag.

Admin Tasks
-----------

User Management
~~~~~~~~~~~~~~~

**View all users:**

- Admin panel shows list of all users
- See auth method (local or SSO)
- See logbook access

**Update user permissions:**

1. Select user from dropdown
2. View current logbook access
3. Hold Ctrl/Cmd to select multiple logbooks
4. Click "Update User Permissions"

**Create local users:**

Use "Register New User" form in admin panel.

Logbook Management
~~~~~~~~~~~~~~~~~~

**Create logbooks:**

Use "Create New Logbook" form.

**Manage logbook access:**

Use "Manage User Logbook Permissions" section to grant/revoke access.

Database Activity
~~~~~~~~~~~~~~~~~

View recent database operations:

1. Go to ``/dbactivity.html``
2. See timestamps, collections, operations
3. Useful for troubleshooting and auditing

Common Workflows
----------------

Shift Log Entry
~~~~~~~~~~~~~~~

1. Login at start of shift
2. Click "Add Entry"
3. Enter: "Shift start - [Your Name] - [Date/Time]"
4. Add keyword: "shift_log"
5. Note any ongoing issues or tasks
6. At end of shift, add another entry with summary

Incident Reporting
~~~~~~~~~~~~~~~~~~

1. Click "Add Entry" immediately
2. Describe the incident clearly
3. Add keywords: "incident", "[system_name]", "[severity]"
4. Attach photos/screenshots if relevant
5. Update entry later with resolution

Equipment Maintenance
~~~~~~~~~~~~~~~~~~~~~

1. Before maintenance: Create entry with plans
2. Keywords: "maintenance", "[equipment_name]"
3. During maintenance: Note observations
4. After maintenance: Update with results
5. Attach before/after photos

Monitoring Trends
~~~~~~~~~~~~~~~~~

1. Go to slow control plots
2. Use range slider to select time period
3. Look for correlations between sensors
4. Screenshot interesting patterns (camera icon)
5. Create logbook entry referencing the time period

Tips and Tricks
---------------

- Use consistent keyword naming (lowercase, underscores)
- Create shift handover templates as keyword sets
- Check slow control plots before/after changes
- Use calendar view to track maintenance schedules
- Export data regularly for backups
- Keep admin password secure and separate from regular users

Troubleshooting
---------------

Can't Add Entry
~~~~~~~~~~~~~~~

- Check you're logged in
- Verify you have logbook access
- Check file sizes (large files may timeout)

Plots Not Loading
~~~~~~~~~~~~~~~~~

- Verify slow control data exists in database
- Check browser console for errors
- Try refreshing page (Ctrl+F5)
- Contact admin to verify data format

Can't See a Logbook
~~~~~~~~~~~~~~~~~~~

- Contact admin to grant access
- Check you selected correct logbook at login
- Verify logbook exists

Search Not Working
~~~~~~~~~~~~~~~~~~

- Clear browser cache
- Try more specific keywords
- Check spelling
- Verify entries exist with those keywords

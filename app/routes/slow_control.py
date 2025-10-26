from flask import Blueprint, render_template, redirect, url_for, session, jsonify
from flask_login import login_required
from bson.objectid import ObjectId
from datetime import datetime, timedelta, timezone
from app import mongo

slow_control = Blueprint('slow_control', __name__)

def make_plot(sensors, plot_title, yaxis_title, hours=72):
    # Build simple Plotly payload from the last N hours of data
    end = datetime.now()#timezone.utc) #+ timedelta(hours=1)
    start = end - timedelta(hours=hours)

    projection = {'timestamp': 1}
    for s in sensors:
        projection[s] = 1

    cursor = mongo.db.slow_control_data.find(
        {'timestamp': {'$gte': start, '$lte': end}},
        projection
    ).sort('timestamp', 1)

    docs = list(cursor)

    traces = []
    for sensor in sensors:
        x, y = [], []
        for doc in docs:
            ts = doc.get('timestamp')
            val = doc.get(sensor)
            if ts is None or val is None:
                continue
            # Ensure UTC-aware and serialize as RFC3339 Z (avoids browser TZ shifts)
            if getattr(ts, 'tzinfo', None) is None:
                ts = ts.replace(tzinfo=timezone.utc)
            x.append(ts.isoformat().replace('+00:00', 'Z'))
            y.append(val)
            
        traces.append({
            'type': 'scatter',
            'mode': 'lines',
            'name': sensor,
            'x': x,
            'y': y
        })

    display_end = end + timedelta(minutes=20)
    layout = {
        'title': {'text': plot_title},
        'uirevision': 'manual-zoom',  # preserve UI state if layout changes later
        'xaxis': {'title': '', 'type': 'date', 'range': [start.isoformat(), display_end.isoformat()]},
        'yaxis': {'title': yaxis_title},
        'height': 250,
        'margin': {'l': 100, 'r': 175, 't': 70, 'b': 30},
    }

    return {'data': traces, 'layout': layout}

def build_plot_payload():
    # Sensor groups
    temperature_in_cryostat = ["TT201", "TT202", "TT203", "TT204", "TT205", "TT206", "TT207", "TT401", "TT402", "TT303", "TT304"]
    pressures = ["PT101", "PT102", "PT103", "PT104", "PT201"]
    pump = ["TT301","TT302","TT103","TT104","FM101","PP401"]
    hv = ["HV_PMT_TOP","HV_PMT_BOT","HV_ANO", "HV_GATE", "HV_CAT", "HV_TS", "HV_BS", "I_PMT_TOP", "I_PMT_BOT"]

    # Plots
    plot_temp1 = make_plot(temperature_in_cryostat, "Temperature", "Temperature (C)")
    plot_pressure1 = make_plot(pressures, "Pressure", "Pressure (bar)")
    plot_pump1 = make_plot(pump, "Pump", "T (C) / F (g/min) / P(W)")
    plot_hv1 = make_plot(hv, "High Voltage", "HV (V)")

    # Latest values (safe handling if no data)
    latest = mongo.db.slow_control_data.find_one(sort=[('timestamp', -1)]) or {}
    selected = ['timestamp', 'PT201', 'TT401', 'TT201', 'TT202', 'FM101']
    units =     ['',        'bar',  'C',     'C',     'C',     'g/min']
    latest_values = {}
    for k, u in zip(selected, units):
        v = latest.get(k)
        if k == 'timestamp' and v is not None and hasattr(v, 'isoformat'):
            v = v.isoformat()
            v = v.replace('T',' ')
        latest_values[k] = (v, u)

    return {
        'plot_temp1': plot_temp1,
        'plot_pressure1': plot_pressure1,
        'plot_pump1': plot_pump1,
        'plot_hv1': plot_hv1,
        'latest_values': latest_values
    }

@slow_control.route('/plot/')
@login_required
def plot_view():
    # Permission check
    logbook_id = ObjectId(session['logbook'])
    logbook = mongo.db.logbooks.find_one({"_id": logbook_id})['name']
    if logbook != 'xams':
        return redirect(url_for('main.index'))

    data = build_plot_payload()
    return render_template('slow_control_plot.html', **data)

@slow_control.route('/plot/data/')
@login_required
def get_plot_data():
    # Permission check
    logbook_id = ObjectId(session['logbook'])
    logbook = mongo.db.logbooks.find_one({"_id": logbook_id})['name']
    if logbook != 'xams':
        return jsonify({'error': 'No permission'}), 403

    data = build_plot_payload()
    resp = jsonify(data)
    resp.headers['Cache-Control'] = 'no-store, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp
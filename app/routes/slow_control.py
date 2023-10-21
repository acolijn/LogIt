import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_login import login_required
from bson.objectid import ObjectId
from app import mongo

import plotly.graph_objects as go
from plotly.offline import plot

slow_control = Blueprint('slow_control', __name__)

@slow_control.route('/plot/')
@login_required
def plot_view():

    # get the name of the logbook from the session
    logbook_id = ObjectId(session['logbook'])
    logbook = mongo.db.logbooks.find_one({"_id": logbook_id})['name']
    if logbook != 'xams':
        # no permission to view this page
        return redirect(url_for('main.show_entries'))

    # Define the temperature sensors you're interested in
    temperature_in_cryostat = ["TT201", "TT202", "TT203", "TT204", "TT205", "TT206", "TT207", "TT401", "TT402"]  # Add as many as you need
    temperature_in_cryostat_plot = make_plot(temperature_in_cryostat, plot_title="Temperature", yaxis_title="Temperature (C)")

    # Define the pressure sensors you're interested in
    pressures = ["PT101", "PT102", "PT103", "PT104", "PT201"]  # Add as many as you need
    pressures_plot = make_plot(pressures, plot_title="Pressure", yaxis_title="Pressure (bar)")

    # Define the pump plots you are interested in
    pump = ["TT301","TT302","TT103","TT104","FM101"]
    pump_plot = make_plot(pump, plot_title="Pump", yaxis_title="Temperature (C) / Flow (g/min)")

    # define
    hv = ["HV_PMT_TOP","HV_PMT_BOT","HV_ANO", "HV_GATE", "HV_CAT", "HV_TS", "HV_BS"]
    hv_plot = make_plot(hv, plot_title="High Voltage", yaxis_title="HV (V)")
	
    # get the last values from the database for a few selected sensors
    latest_data = mongo.db.slow_control_data.find_one(sort=[('timestamp', -1)])

    # Extract the last measured values of the variables you are interested in
    selected_variables = ['timestamp', 'PT201', 'TT401', 'TT201', 'TT202', 'FM101']  # add your variables here
    selected_variables_units = ['','bar', 'C', 'C', 'C', 'g/min']
    
    latest_values_with_units = {var: (latest_data[var], unit) for var, unit in zip(selected_variables, selected_variables_units)}

    return render_template('slow_control_plot.html', 
                           plot_temp1=temperature_in_cryostat_plot, 
                           plot_pressure1=pressures_plot,
                           plot_pump1=pump_plot,
                           plot_hv1=hv_plot,
                           latest_values=latest_values_with_units)

@login_required
def make_plot(sensors, plot_title, yaxis_title):
    """Make a plot of the sensor data.	

    Args:
        sensors (list): The list of sensors to plot.
        plot_title (str): The title of the plot.
        yaxis_title (str): The title of the y-axis.
        
    Returns:
        str: The plotly plot as HTML div.

    """
    cursor = mongo.db.slow_control_data.find({}).sort('timestamp', 1)

    # Initialize the dictionary to store sensor data
    sensor_data = {sensor: [] for sensor in sensors}

    timestamps = []

    for doc in cursor:
        timestamps.append(doc['timestamp'])
        
        for sensor in sensors:
            if sensor in doc:
                sensor_data[sensor].append(doc[sensor])
            else:
                sensor_data[sensor].append(0)

    # Create traces for each sensor
    traces = [
        go.Scatter(
            x=timestamps,
            y=sensor_data[sensor],
            mode='lines',
            name=sensor
        ) for sensor in sensors
    ]

    # plot layout

    
    layout = go.Layout(
        title=plot_title,
        #xaxis=dict(title='Time'),
        yaxis=dict(title=yaxis_title),
        height=250,
        margin=go.layout.Margin(
            l=100,  # Left margin
            r=300,  # Right margin
            b=0,  # Bottom margin
            t=30,  # Top margin
            pad=4  # Sets the amount of padding (in px) between the plotting area and the axis lines
        )
    )

    fig = go.Figure(data=traces, layout=layout)
    fig.update_layout(autosize=True)

    plot_div = plot(fig, output_type='div')

    return plot_div
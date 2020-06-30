import datetime
import time
import json

import sqlite3

from flask import Flask, render_template, request, Response, redirect, url_for
from flask.json import jsonify

from config import Config

from sensors.forms.forms import SensorForm, CustomSearchForm, ReadingForm
from sensors.validators.validators import reading_is_valid, is_valid_type, CUSTOM_SEARCH_ERRORS

from flask_bootstrap import Bootstrap

from statistics import median_high, mean
import numpy as np


app = Flask(__name__)
app.config.from_object(Config)
Bootstrap(app)

client = app.test_client

# Setup the SQLite DB
conn = sqlite3.connect('database.db')
# conn.execute('DROP TABLE IF EXISTS readings')
conn.execute('CREATE TABLE IF NOT EXISTS readings (device_uuid TEXT, type TEXT, value INTEGER, date_created INTEGER)')
conn.close()


# ----- USER INTERFACE SECTION -----


@app.route('/', methods=['GET'])
def index():
    """
        This function returns the sensors registered in the database (UI)
    """
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute('select distinct device_uuid from readings order by date_created')
    rows = cur.fetchall()

    sensors = jsonify([dict(zip(['device_uuid'], row)) for row in rows])

    form = SensorForm()
    custom_search_form = CustomSearchForm()

    return render_template('index.html', sensors=sensors, form=form, custom_search_form=custom_search_form)


@app.route('/readings/<string:device_uuid>/', methods=['POST', 'GET'])
def ui_request_device_readings(device_uuid):
    """
    This function allows clients to POST or GET data specific sensor types (UI)

    POST Parameters:
    * type -> The type of sensor (temperature or humidity)
    * value -> The integer value of the sensor reading
    * date_created -> The epoch date of the sensor reading.
        If none provided, we set to now.

    Optional Query Parameters:
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    * type -> The type of sensor value a client is looking for
    """

    form = ReadingForm()

    if request.method == 'POST':
        form_json = {
            'date_created': request.form.get('date_created'),
            'type': request.form.get('type'),
            'value': request.form.get('value'),
        }
        response = client().post('/devices/{}/readings/'.format(device_uuid), data=json.dumps(form_json))
        if response.status_code == 201:
            # Return success
            return redirect(url_for('ui_request_device_readings', device_uuid=device_uuid))
        else:
            return redirect(url_for('ui_request_device_readings', device_uuid=device_uuid, error=response.data))

    else:
        readings = client().get('/devices/{}/readings/'.format(device_uuid))
        return render_template('detail.html', sensors=readings, device_uuid=device_uuid, form=form)


@app.route('/new/<string:device_uuid>/', methods=['POST'])
def ui_register_new_sensor(device_uuid):
    """
    This function allows clients to POST a new sensor data. (UI)

    POST Parameters:
    * type -> The type of sensor (temperature or humidity)
    * value -> The integer value of the sensor reading
    * date_created -> The epoch date of the sensor reading.
        If none provided, we set to now.
    """

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Grab the post parameters
    sensor_type = request.form.get('type')
    value = request.form.get('value')
    date_created = request.form.get('date_created')

    is_valid, result = reading_is_valid(sensor_type, value)

    if is_valid:
        # Insert data into db
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (device_uuid, sensor_type, value, date_created))

        conn.commit()

        # Return success
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index', error=result))


@app.route('/custom/search/', methods=['POST'])
def ui_get_readings_by_type_or_date_range():
    """
    This endpoint allows clients to GET sensors readings by type or date range.

    Optional Query Parameters
    * type -> The type of sensor value a client is looking for
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    """
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Grab the post parameters
    selected_type = request.form.get('available_types')

    if int(selected_type) == 0:
        type = request.form.get('type')
        selected_search = 'Sensor Type: ' + type.capitalize()
        cur.execute('select * from readings where type="{}"'.format(type))
    elif int(selected_type) == 1:
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        selected_search = 'Date Range: Start: ' + start_date + ' End: ' + end_date
        start_date_time_obj = int(datetime.datetime.strptime(start_date, '%d/%m/%Y').timestamp())
        end_date_time_obj = int(datetime.datetime.strptime(end_date, '%d/%m/%Y').replace(
            hour=23, minute=59, second=59).timestamp())
        cur.execute('select * from readings where date_created>="{}" and date_created<="{}"'.format(
            start_date_time_obj, end_date_time_obj))
    else:
        return redirect(url_for('index', custom_search_error=CUSTOM_SEARCH_ERRORS[0]))

    rows = cur.fetchall()

    sensors = jsonify([dict(zip(['device_uuid', 'type', 'value', 'date_created'], row)) for row in rows])

    return render_template('search_results.html', sensors=sensors, selected_search=selected_search)


@app.route('/readings/<string:device_uuid>/max', methods=['GET'])
def ui_get_readings_max(device_uuid):
    """
    This function allows clients to POST or GET data specific sensor types (UI)

    POST Parameters:
    * type -> The type of sensor (temperature or humidity)
    * value -> The integer value of the sensor reading
    * date_created -> The epoch date of the sensor reading.
        If none provided, we set to now.

    Optional Query Parameters:
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    * type -> The type of sensor value a client is looking for
    """

    form = ReadingForm()

    reading = client().get('/devices/{}/readings/max/'.format(device_uuid))
    return render_template('detail.html', sensors=reading, device_uuid=device_uuid, form=form)


@app.route('/readings/<string:device_uuid>/median', methods=['GET'])
def ui_get_readings_median(device_uuid):
    """
    This function allows clients to POST or GET data specific sensor types (UI)

    POST Parameters:
    * type -> The type of sensor (temperature or humidity)
    * value -> The integer value of the sensor reading
    * date_created -> The epoch date of the sensor reading.
        If none provided, we set to now.

    Optional Query Parameters:
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    * type -> The type of sensor value a client is looking for
    """

    form = ReadingForm()

    reading = client().get('/devices/{}/readings/median/'.format(device_uuid))
    return render_template('detail.html', sensors=reading, device_uuid=device_uuid, form=form)


@app.route('/readings/<string:device_uuid>/mean', methods=['GET'])
def ui_get_readings_mean(device_uuid):
    """
    This function allows clients to POST or GET data specific sensor types (UI)

    POST Parameters:
    * type -> The type of sensor (temperature or humidity)
    * value -> The integer value of the sensor reading
    * date_created -> The epoch date of the sensor reading.
        If none provided, we set to now.

    Optional Query Parameters:
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    * type -> The type of sensor value a client is looking for
    """

    form = ReadingForm()

    reading = client().get('/devices/{}/readings/mean/'.format(device_uuid))
    return render_template('detail.html', sensors=reading, device_uuid=device_uuid, form=form)


@app.route('/readings/<string:device_uuid>/quartiles', methods=['GET'])
def ui_get_readings_quartiles(device_uuid):
    """
    This function allows clients to POST or GET data specific sensor types (UI)

    POST Parameters:
    * type -> The type of sensor (temperature or humidity)
    * value -> The integer value of the sensor reading
    * date_created -> The epoch date of the sensor reading.
        If none provided, we set to now.

    Optional Query Parameters:
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    * type -> The type of sensor value a client is looking for
    """

    form = ReadingForm()

    readings = client().get('/devices/{}/readings/quartiles/'.format(device_uuid))
    return render_template('detail.html', sensors=readings, device_uuid=device_uuid, form=form)


@app.route('/readings/summary', methods=['GET'])
def ui_get_summary():
    """
    This function allows clients to POST or GET data specific sensor types (UI)

    POST Parameters:
    * type -> The type of sensor (temperature or humidity)
    * value -> The integer value of the sensor reading
    * date_created -> The epoch date of the sensor reading.
        If none provided, we set to now.

    Optional Query Parameters:
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    * type -> The type of sensor value a client is looking for
    """

    form = ReadingForm()

    readings = client().get('/summary/')
    return render_template('detail.html', sensors=readings, device_uuid='Summary', form=form)


# ----- ENDPOINTS SECTION -----


@app.route('/devices/<string:device_uuid>/readings/', methods=['POST', 'GET'])
def request_device_readings(device_uuid):
    """
    This endpoint allows clients to POST or GET data specific sensor types.

    POST Parameters:
    * type -> The type of sensor (temperature or humidity)
    * value -> The integer value of the sensor reading
    * date_created -> The epoch date of the sensor reading.
        If none provided, we set to now.

    Optional Query Parameters:
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    * type -> The type of sensor value a client is looking for
    """

    # Set the db that we want and open the connection
    if app.config['TESTING']:
        conn = sqlite3.connect('test_database.db')
    else:
        conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if request.method == 'POST':
        # Grab the post parameters
        post_data = json.loads(request.data)
        sensor_type = post_data.get('type')
        value = post_data.get('value')
        date_created = post_data.get('date_created', int(time.time()))

        is_valid, result = reading_is_valid(sensor_type, value)

        if is_valid:
            # Insert data into db
            cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                        (device_uuid, sensor_type, value, date_created))

            conn.commit()

            # Return success
            return 'success', 201
        else:
            return result, 400
    else:
        # Execute the query
        cur.execute('select * from readings where device_uuid="{}"'.format(device_uuid))
        rows = cur.fetchall()

        # Return the JSON
        return jsonify([dict(zip(['device_uuid', 'type', 'value', 'date_created'], row)) for row in rows]), 200


@app.route('/custom/search/<string:option>', methods=['POST'])
def get_readings_by_type_or_date_range(option):
    """
    This endpoint allows clients to GET sensors readings by type or date range.

    Optional Query Parameters
    * type -> The type of sensor value a client is looking for
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    """
    # Set the db that we want and open the connection
    if app.config['TESTING']:
        conn = sqlite3.connect('test_database.db')
    else:
        conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Grab the post parameters
    selected_type = option

    post_data = json.loads(request.data)

    if selected_type == 'type':
        reading_type = post_data.get('type')
        is_valid, result = is_valid_type(reading_type)
        if is_valid:
            cur.execute('select * from readings where type="{}"'.format(reading_type))
        else:
            return result, 400
    elif selected_type == 'range':
        start_date = post_data.get('start_date')
        end_date = post_data.get('end_date')
        cur.execute('select * from readings where date_created>="{}" and date_created<="{}"'.format(
            start_date, end_date))
    else:
        return CUSTOM_SEARCH_ERRORS[0], 400

    rows = cur.fetchall()

    return jsonify([dict(zip(['device_uuid', 'type', 'value', 'date_created'], row)) for row in rows]), 200


@app.route('/devices/<string:device_uuid>/readings/max/', methods=['GET'])
def request_device_readings_max(device_uuid):
    """
    This endpoint allows clients to GET the max sensor reading for a device.

    Mandatory Query Parameters:
    * type -> The type of sensor value a client is looking for

    Optional Query Parameters
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    """

    # Set the db that we want and open the connection
    if app.config['TESTING']:
        conn = sqlite3.connect('test_database.db')
    else:
        conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Execute the query
    cur.execute('select device_uuid, type, max(value), date_created from readings where device_uuid="{}"'.format(
        device_uuid))
    rows = cur.fetchall()

    # Return the JSON
    return jsonify([dict(zip(['device_uuid', 'type', 'value', 'date_created'], row)) for row in rows]), 200


@app.route('/devices/<string:device_uuid>/readings/median/', methods=['GET'])
def request_device_readings_median(device_uuid):
    """
    This endpoint allows clients to GET the median sensor reading for a device.

    Mandatory Query Parameters:
    * type -> The type of sensor value a client is looking for

    Optional Query Parameters
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    """

    # Set the db that we want and open the connection
    if app.config['TESTING']:
        conn = sqlite3.connect('test_database.db')
    else:
        conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Execute the query
    cur.execute('select * from readings where device_uuid="{}" order by value'.format(device_uuid))
    rows = cur.fetchall()

    values = []

    readings = jsonify([dict(zip(['device_uuid', 'type', 'value', 'date_created'], row)) for row in rows]).json

    for json in readings:
        values.append(json.get('value'))

    readings_median_value = median_high(values)

    median_reading = list(filter(lambda x: x["value"] == readings_median_value, readings))

    # Return the JSON
    return jsonify(median_reading), 200


@app.route('/devices/<string:device_uuid>/readings/mean/', methods = ['GET'])
def request_device_readings_mean(device_uuid):
    """
    This endpoint allows clients to GET the mean sensor readings for a device.

    Mandatory Query Parameters:
    * type -> The type of sensor value a client is looking for

    Optional Query Parameters
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    """

    # Set the db that we want and open the connection
    if app.config['TESTING']:
        conn = sqlite3.connect('test_database.db')
    else:
        conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Execute the query
    cur.execute('select * from readings where device_uuid="{}" order by value'.format(device_uuid))
    rows = cur.fetchall()

    values = []

    readings = jsonify([dict(zip(['device_uuid', 'type', 'value', 'date_created'], row)) for row in rows]).json

    for json in readings:
        values.append(json.get('value'))

    readings_mean_value = mean(values)

    # Return the JSON
    return jsonify({'value': readings_mean_value}), 200


@app.route('/devices/<string:device_uuid>/readings/quartiles/', methods=['GET'])
def request_device_readings_quartiles(device_uuid):
    """
    This endpoint allows clients to GET the 1st and 3rd quartile
    sensor reading value for a device.

    Mandatory Query Parameters:
    * type -> The type of sensor value a client is looking for
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    """

    # Set the db that we want and open the connection
    if app.config['TESTING']:
        conn = sqlite3.connect('test_database.db')
    else:
        conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Execute the query
    cur.execute('select * from readings where device_uuid="{}" order by value'.format(device_uuid))
    rows = cur.fetchall()

    values = []

    readings = jsonify([dict(zip(['device_uuid', 'type', 'value', 'date_created'], row)) for row in rows]).json

    for json in readings:
        values.append(json.get('value'))

    quantile1 = np.quantile(values, 0.25)
    quantile3 = np.quantile(values, 0.75)

    # Return the JSON
    return jsonify({'quartile_1': quantile1, 'quartile_3': quantile3}), 200


@app.route('/summary/', methods=['GET'])
def request_readings_summary():
    """
    This endpoint allows clients to GET a full summary
    of all sensor data in the database per device.

    Optional Query Parameters
    * type -> The type of sensor value a client is looking for
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    """

    # Set the db that we want and open the connection
    if app.config['TESTING']:
        conn = sqlite3.connect('test_database.db')
    else:
        conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Execute the query
    cur.execute('select distinct device_uuid from readings')
    rows = cur.fetchall()

    sensors = jsonify([dict(zip(['device_uuid'], row)) for row in rows])

    readings_json_array = []

    for sensor in sensors.json:
        device_uuid = sensor.get('device_uuid')
        cur.execute('select count(value) as count, max(value) as max from readings where device_uuid="{}"'.format(device_uuid))
        rows = cur.fetchall()

        count_max_readings = jsonify([dict(zip(['count', 'max'], row)) for row in rows]).json[0]
        number_of_readings = count_max_readings.get('count')
        max_reading_value = count_max_readings.get('max')

        cur.execute('select * from readings where device_uuid="{}" order by value'.format(device_uuid))
        rows = cur.fetchall()

        values = []

        readings = jsonify([dict(zip(['device_uuid', 'type', 'value', 'date_created'], row)) for row in rows]).json

        for json in readings:
            values.append(json.get('value'))

        readings_median_value = median_high(values)
        readings_mean_value = mean(values)
        quantile1 = np.quantile(values, 0.25)
        quantile3 = np.quantile(values, 0.75)

        readings_json_array.append({'device_uuid': device_uuid, 'number_of_readings': number_of_readings,
                                    'max_reading_value': max_reading_value, 'median_reading_value': readings_median_value,
                                    'mean_reading_value': readings_mean_value, 'quartile_1_value': quantile1,
                                    'quartile_3_value': quantile3})

    return jsonify(readings_json_array), 200


if __name__ == '__main__':
    app.run()

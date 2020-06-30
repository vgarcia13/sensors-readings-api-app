from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, DateTimeField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional
from wtforms.widgets import html5 as h5widgets

import datetime
import time
import uuid

__author__ = 'vgarcia'


def generate_uuid():
    return uuid.uuid1()


def generate_timestamp():
    return int(time.time())


def timestamp_to_date():
    timestamp = generate_timestamp()
    date = datetime.datetime.utcfromtimestamp(timestamp)
    return date


class SensorForm(FlaskForm):
    date_created = IntegerField('Date Created', default=generate_timestamp)
    device_uuid = StringField('Device UUID', validators=[DataRequired()], default=generate_uuid)
    type = SelectField('Reading Type', choices=[('temperature', 'Temperature'), ('humidity', 'Humidity')],
                       validators=[DataRequired()])
    value = IntegerField('Value', validators=[DataRequired()], widget=h5widgets.NumberInput(min=0, max=100, step=1))
    submit = SubmitField('Submit')


class CustomSearchForm(FlaskForm):
    available_types = SelectField('Search by:', choices=[(0, 'Type'), (1, 'Date range')])
    type = SelectField('Reading Type', choices=[('temperature', 'Temperature'), ('humidity', 'Humidity')],
                       validators=[Optional()])
    start_date = DateTimeField('Start Date', format='%d/%m/%Y', default=timestamp_to_date,
                               validators=[Optional()])
    end_date = DateTimeField('End Date', format='%d/%m/%Y', default=timestamp_to_date,
                             validators=[Optional()])
    submit = SubmitField('Submit')


class ReadingForm(FlaskForm):
    date_created = IntegerField('Date Created', default=generate_timestamp)
    type = SelectField('Reading Type', choices=[('temperature', 'Temperature'), ('humidity', 'Humidity')],
                       validators=[DataRequired()])
    value = IntegerField('Value', validators=[DataRequired()], widget=h5widgets.NumberInput(min=0, max=100, step=1))
    submit = SubmitField('Submit')

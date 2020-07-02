# Sensor readings API Application

## Introduction
This is a code exercise about an API application that register, retrieve and get different reading statistics depending
of a certain device UUID, search parameters (type or date range) and a general summary endpoint.

## API Documentation
The complete endpoints list of the APi app:

1.  `/devices/<device_uuid>/readings/', methods=['POST', 'GET']`
        
    This endpoint can register a new sensor reading or retrieve sensor readings

    Test request (POST):
    
        {
            "type": "temperature",
            "value": "98",
            "date_created": 1593550061
        }
    Response:
    
        {
            "date_created": 1593543759,
            "device_uuid": "44875d62-bb04-11ea-be83-a886dd916590",
            "type": "temperature",
            "value": 14
        }

2.  `/custom/search/<option>', methods=['POST']`

    This endpoint allows custom readings search (by type [temperature, humidity] or by date range [start date, end date])
    
    AVAILABLE SEARCH PARAMETERS (OPTION URL PARAMETER): 
    
    - `type` for reading type (temperature, humidity)
    - `range` for date range (start date, end date) 
    
    Test request (POST):
    
        {
            "type": "temperature",
            "start_date": "",
            "end_date": ""
        }
        
        {
            "type": "",
            "start_date": "01/06/2020",
            "end_date": "30/06/2020"
        }
    Response:
    
        {
            "date_created": 1593543759,
            "device_uuid": "44875d62-bb04-11ea-be83-a886dd916590",
            "type": "temperature",
            "value": 14
        }
    
3.  `/devices/<device_uuid>/readings/max/', methods=['GET']`

    This endpoint returns the MAX reading of a specific device_UUID`
    
    Response (GET):
    
        {
            "date_created": 1593550061,
            "device_uuid": "44875d62-bb04-11ea-be83-a886dd916590",
            "type": "temperature",
            "value": 98
        }

4.  `/devices/<device_uuid>/readings/median/', methods=['GET']`

    This endpoint returns the MEDIAN reading of a specific device_UUID
    
    Response (GET):
    
        {
            "date_created": 1593543804,
            "device_uuid": "44875d62-bb04-11ea-be83-a886dd916590",
            "type": "humidity",
            "value": 52
        }

5.  `/devices/<device_uuid>/readings/mean/', methods=['GET']`

    This endpoint returns the MEAN reading of a specific device_UUID
    
    Response (GET):
    
        {
            "value": 44
        }
        
6. `/devices/<device_uuid>/readings/quartiles/', methods=['GET']`

    This endpoint returns the 1st and 3rd quartiles of a specific device_UUID readings 
    
    Response (GET):
    
        {
            "quartile_1": 13.5,
            "quartile_3": 63.5
        }
        
7.  `/summary/', methods=['GET']`

    This endpoint returns the a summary of all sensors registered, with statistics and general info
    
    Response (GET):
    
        {
            "device_uuid": "44875d62-bb04-11ea-be83-a886dd916590",
            "max_reading_value": 98,
            "mean_reading_value": 44,
            "median_reading_value": 52,
            "number_of_readings": 4,
            "quartile_1_value": 13.5,
            "quartile_3_value": 63.5
        },
        {
            "device_uuid": "471d9000-bb04-11ea-82af-a886dd916590",
            "max_reading_value": 99,
            "mean_reading_value": 77.33333333333333,
            "median_reading_value": 88,
            "number_of_readings": 3,
            "quartile_1_value": 66.5,
            "quartile_3_value": 93.5
        }

## Installation

1. Clone this repo
2. Create a new virtual environment (with `Python3.6.7` preferred or above) and active it
3. Run (with virtual env activated) `pip install -r requirements.txt` (to install project's dependencies)
4. Configure a valid Flask server
5. Run the project

## User UI
There is an user interface that interacts with this API, made with ``Flask`` ``HTML5`` and `Bootstrap 4`

To access this interface, go to the project root `/` in your browser (`Flask` server running)

or 

[Use the live demo here](https://vgarcia-sensors-reads-api-app.herokuapp.com/)

## Testing
Tests can be run via `pytest -v`

## How was designed and implemented?

I decided to design and implement an user interface because I really think there is too much value in an API app if the results
are shown and being used in a running app, and also to practice my full-stack skills

The endpoints are very clear to understand and the comments inside every function help any developer to change and improve this project

The entire API app can be tested in `Postman` or any other API tester

I would prioritize the way the sensors are configured and protected, because there can be some issues working with 
hardware devices that deliver data to a software. 

Afterwards I would ensure the API to always get the data from a known source, in order to treat and deliver trusting info,
adding some web tokens, authorizations headers inside request or a login stage

## About the author
Mechatronics engineer graduated from Universidad Iberoamericana, with more than 6 years of experience in IT and programming in general (web, mobile). 

Advanced english (IELTS and EF Standard English Test certified), experience with international teams and managing small developing teams

More information:

LinkedIn Page: https://www.linkedin.com/in/victor-hugo-garcia-202b1b99/


&copy; Copyright 2020
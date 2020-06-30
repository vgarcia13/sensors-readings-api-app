TEMPERATURE = 'temperature'
HUMIDITY = 'humidity'

READINGS_TYPES = [TEMPERATURE, HUMIDITY]
READINGS_TYPES_ERRORS = ['NOT_VALID_TYPE', 'READING_OUT_OF_RANGE']
CUSTOM_SEARCH_ERRORS = ['NOT_VALID_SEARCHING_TYPE']

__author__ = 'vgarcia'


def reading_is_valid(type, value):
    if type not in READINGS_TYPES:
        return False, READINGS_TYPES_ERRORS[0]
    elif int(value) not in range(0, 101):
        return False, READINGS_TYPES_ERRORS[1]
    else:
        return True, ''


def is_valid_type(type):
    if type not in READINGS_TYPES:
        return False, READINGS_TYPES_ERRORS[0]
    else:
        return True, ''

from datetime import datetime, timedelta


def keys2DatetimeObj(datetime_dict):

    datetimeList = list(datetime_dict.keys())

    # Define the format of your date string
    date_format = "%Y-%m-%d %H:%M:%S.%f"

    # Parse the string into a datetime object
    date_object = [datetime.strptime(datetimeElement, date_format)
                   for datetimeElement in datetimeList]
    return date_object

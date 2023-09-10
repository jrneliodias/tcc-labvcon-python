from controladores_views.pid_view import *
from controladores_views.gmv_view import *
from controladores_views.gpc_view import *
from controladores_views.imc_view import *
from connections import *
from mainSideBar import *
from session_state import *
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from datetime import datetime, timedelta


def keys2DatetimeObj(datetime_dict):

    datetimeList = list(datetime_dict.keys())

    # Define the format of your date string
    date_format = "%Y-%m-%d %H:%M:%S.%f"

    # Parse the string into a datetime object
    date_object = [datetime.strptime(datetimeElement, date_format)
                   for datetimeElement in datetimeList]
    return date_object

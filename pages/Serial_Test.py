from connections import *
from components import *
from session_state import *
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from formatterInputs import *


st.set_page_config(
    page_title="Ex-stream-ly Cool App",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",

)
loadSessionStates()




def datetime_obj_to_elapsed_time(variable:str)->dict:

    sensor_data_dict = get_session_variable(variable)
    date_object = keys2DatetimeObj(sensor_data_dict)

    time_interval = [0] + [(date_object[i] - date_object[0]).total_seconds()
                           for i in range(1, len(date_object))]

    # sensor_formatted2Hours_dict = {
    #     key.split()[1]: value
    #     for key, value in sensor_dict.items()
    # }

    elapsed_time_in_sec = {time_interval[i]: sensor_data_dict[key]
                           for i, key in enumerate(sensor_data_dict)}
    

    return elapsed_time_in_sec

def dictionary_to_pandasDataframe(variable:dict,variable_name_column:str)->pd.DataFrame:

    # Convert the inner dictionary to a list of dictionaries
    data_list = [{"Time (s)": timestamp, f"{variable_name_column}": value} for timestamp, value in variable.items()]

    # Create a DataFrame from the list of dictionaries
    variable_dataframe = pd.DataFrame(data_list)
    return variable_dataframe

def insertReferenceInDataframe(variable_dataframe:pd.DataFrame,reference_col:list)->pd.DataFrame:

    # Convert the inner dictionary to a list of dictionaries
    variable_dataframe['Reference'] = reference_col

    return variable_dataframe

def dataframeToPlot(variable_dict:str,variable_name_to_plot:str, second_variable:str) -> pd.DataFrame:
    if not datetime_obj_to_elapsed_time(variable_dict):
        return
    
    variable_with_time = datetime_obj_to_elapsed_time(variable_dict)
    process_dictionary = dictionary_to_pandasDataframe(variable_with_time,variable_name_to_plot)
    return insertReferenceInDataframe(process_dictionary,get_session_variable(second_variable))

def plot_chart_validation(plot_variable,y:str,height= 200, x = 'Time (s)'):
    if plot_variable is None:
        return None
    if plot_variable.empty:
        return None
    
    return st.line_chart(data= plot_variable,x = x, y = y,height=height)


st.title('LABVCON - Laboratório Virtual de Controle')
st.header('Teste da comunicação Serial', divider='rainbow')


# SideBar
with st.sidebar:
    sidebarMenu()
    st.session_state

open_loop_process_output = datetime_obj_to_elapsed_time('process_output_sensor')
ol_output_dataframe = dictionary_to_pandasDataframe(open_loop_process_output,'Open Loop')
        
        
plot_chart_validation(ol_output_dataframe, x = 'Time (s)', y = 'Open Loop',height=500)



col1, col2 = st.columns(2)

with col1:

    datetimeList = list(st.session_state.sensor.keys())

    # Define the format of your date string
    date_format = "%Y-%m-%d %H:%M:%S.%f"

    # Parse the string into a datetime object
    date_object = [datetime.strptime(datetimeElement, date_format)
                   for datetimeElement in datetimeList]

    time_interval = [(date_object[i] - date_object[i-1]).total_seconds()
                     for i in range(1, len(date_object))]

    st.line_chart(time_interval)

with col2:

    if time_interval:
        'Média do intervalo'
        mean_value = sum(time_interval) / len(time_interval)
        mean_value
        'Média do erro'
        mean_error = sum(abs(x - mean_value)
                         for x in time_interval) / len(time_interval)
        mean_error

    'Tempo da simulação'
    if date_object:
        date_object[-1] - date_object[0]



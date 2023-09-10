from controladores_views.controller_imports import *


st.set_page_config(
    page_title="Ex-stream-ly Cool App",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",

)

loadSessionStates()

st.header('LABVCON - Laboratório Virtual de Controle', divider='rainbow')
selectMethod = option_menu(
    menu_title=None,
    options=['PID', 'IMC', 'GMV', 'GPC'],
    orientation='horizontal',
    icons=['diagram-2', 'ui-radios-grid',
           'app', 'command'],

)


case_functions = {
    "PID": pid_Controller,
    "IMC": imc_Controller,
    "GMV": gmv_Controller,
    "GPC": gpc_Controller,
}

case_functions[selectMethod]()


# SideBar
with st.sidebar:
    mainSidebarMenu()
    st.session_state

##########################################################################

sensor_dict = st.session_state.sensor

sensor_formatted2Hours_dict = {
    key.split()[1]: value
    for key, value in sensor_dict.items()
}

st.line_chart(data=sensor_formatted2Hours_dict)

#########################################################################
col1, col2 = st.columns(2)
date_object = keys2DatetimeObj(sensor_dict)

with col1:

    time_interval = [(date_object[i] - date_object[i-1]).total_seconds()
                     for i in range(1, len(date_object))]

    st.line_chart(time_interval)

with col2:

    if time_interval:

        '### Tempo da simulação'
        if date_object:
            time = date_object[-1] - date_object[0]
            st.write(f'{time.total_seconds()} seconds')

        'Média do intervalo'
        mean_value = sum(time_interval) / len(time_interval)
        mean_value

        'Média do erro'
        mean_error = sum(abs(x - mean_value)
                         for x in time_interval) / len(time_interval)
        mean_error/st.session_state.sampling_time

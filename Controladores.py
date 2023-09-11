from controladores_views.controller_imports import *


st.set_page_config(
    page_title="Ex-stream-ly Cool App",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",

)

add_logo("images/app_logo2.png", height=150)
loadSessionStates()

st.header('LABVCON - Laboratório Virtual de Controle', divider='rainbow')
selectMethod = option_menu(
    menu_title=None,
    options=['PID', 'IMC', 'GMV', 'GPC'],
    orientation='horizontal',
    icons=['diagram-2', 'ui-radios-grid',
           'app', 'command'],

)

##########################################################################

# SideBar
with st.sidebar:
    mainSidebarMenu()
    with st.expander("Session States:"):
        st.session_state

##########################################################################


case_functions = {
    "PID": pid_Controller,
    "IMC": imc_Controller,
    "GMV": gmv_Controller,
    "GPC": gpc_Controller,
}

case_functions[selectMethod]()

##########################################################################

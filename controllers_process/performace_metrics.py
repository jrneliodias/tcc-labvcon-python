from session_state import get_session_variable
import numpy as np

def integrated_absolute_error()->float:
    reference_input = get_session_variable['reference_input'] 
    process_output_sensor = get_session_variable['process_output_sensor'] 
    
    # Calculate absolute difference element-wise
    absolute_error = np.abs(reference_input - process_output_sensor)
    sum_absolute_error = np.sum(absolute_error)
    return sum_absolute_error
    

def total_variation_control(control_signal:str)->float:
    
    control_values = get_session_variable(control_signal)
    control_variation = np.diff(control_values)
    total_control_variation = np.sum(control_variation)
    return total_control_variation
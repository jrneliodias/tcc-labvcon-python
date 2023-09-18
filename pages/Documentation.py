import numpy as np
import streamlit as st


def get_sample_position(sampling_time, samples_number, time_instant):
    """
    Calculate the position (index) of a given time instant in the sampled data.

    Parameters:
    - sampling_time: The time between each sample.
    - samples_number: The total number of samples.
    - time_instant: The time instant for which you want to find the sample position.

    Returns:
    - The position (index) of the sample corresponding to the given time instant.
    """
    if time_instant < 0:
        return 0  # Handle negative time instant

    # Calculate the position based on the time instant and sampling time
    position = int(time_instant / sampling_time)

    # Ensure the position is within the valid range [0, samples_number-1]
    position = max(0, min(position, samples_number - 1))

    return position


# Example usage:
# Example sampling time (e.g., 0.1 seconds between samples)
sampling_time = 0.01
samples_number = 1000  # Example total number of samples
time_instant = 2.7  # Example time instant for which you want to find the sample position

time_interval = np.arange(0.0, sampling_time*samples_number, sampling_time)

st.write(time_interval)

sample_position = get_sample_position(
    sampling_time, samples_number, time_instant)
st.write(f"Sample position at time {time_instant} is {sample_position}")

time_interval[sample_position]

# IMPORTING REQUIRED LIBRARIES

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL = ("C:/Users/Abishek.S/Desktop/Vehicle collision dashboard/Motor_Vehicle_Collisions_-_Crashes.csv")

dataset_link = "https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95"

st.set_page_config(page_title='NY City Vehicle Collision Analysis')

st.title("***New York City Vehicle Collision Analysis***")
st.markdown('---')
st.markdown("***This application acts as an interactive Dashboard which analyzes the motor vehicle collisions in NYC using the [New York City Vehicle Collision](%s) data set from July 4th,2023.***" % dataset_link)


@st.cache_data(persist=True, show_spinner=False)
def load_data(rows):
    data = pd.read_csv(DATA_URL, parse_dates=[['CRASH DATE' , 'CRASH TIME']], nrows=rows)
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    data = data[(data.LATITUDE != 0) & (data.LONGITUDE > -80)]
    data.rename(columns={'CRASH DATE_CRASH TIME': 'DATE/TIME'}, inplace=True)
    lower_case = lambda x : str(x).lower()
    data.rename(lower_case, axis='columns', inplace=True)
    return data

data = load_data(100000)
original_data = data

st.header("Where are the most people injured in New York City?")
injured_people = st.slider("Number of people injured in vehicle collisions", 0, 19)
st.map(data.query("@data['number of persons injured'] >= @injured_people")[["latitude", "longitude"]].dropna(how="any"))

st.markdown('---')

st.header("How many collisions occur during a given time of day?: 3-D Map of Vehicle Collisions by Time of Day")
hour = st.slider("Select hour range to view data on:", 0, 23, (8,18), key='sld_time')
data = data[data['date/time'].dt.hour == hour]

st.header("How many collisions occur during a given time of day?")
hour = st.slider("Hour to look at", 0, 23)
data = data[data['date/time'].dt.hour == hour]

st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour, (hour + 1) % 24))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state = {
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50
    },
    layers = [
        pdk.Layer(
            "HexagonLayer",
            data = data[['date/time', 'latitude', 'longitude']],
            get_position=['longitude', 'latitude'],
            radius=100,
            extruded=True,
            pickable=True,
            elevation_scale=4,
            elevation_range=[0, 1000],
        ),
    ],
))


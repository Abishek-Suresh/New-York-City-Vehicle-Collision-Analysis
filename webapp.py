# IMPORTING REQUIRED LIBRARIES

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL = ("Motor_Vehicle_Collisions_-_Crashes.csv")
st.set_page_config(page_title='NY City Vehicle Collision Analysis')

dataset_link = "https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95"


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

@st.cache_data(experimental_allow_widgets=True, show_spinner=False)
def filter_by_injuries(injury_count):
    res = data.query("@data['number of persons injured'] >= @injury_count")[['latitude', 'longitude']]
    return res

@st.cache_data(experimental_allow_widgets=True, show_spinner=False)
def filter_by_hour_map(hour_filter):
    data_filtered = (data[(data['date/time'].dt.hour >= hour_filter[0]) & (data['date/time'].dt.hour <= hour_filter[1])][['date/time', 'latitude', 'longitude']])
    return(
        pdk.Deck(
            map_style='mapbox://styles/mapbox/streets-v11',
            initial_view_state={
                'latitude': data.latitude.mean(),
                'longitude': data.longitude.mean(),
                'zoom': 9.6,
                'pitch': 50
            },
            layers=[
                pdk.Layer(
                    'HexagonLayer',
                    data=data_filtered,
                    get_position=['longitude', 'latitude'],
                    radius=100,
                    extruded=True,
                    pickable=True,
                    elevation_scale=4,
                    elevation_range=[0,1000]
                )
            ]
        )
    )

@st.cache_data(persist=True, show_spinner=False)
def collision_hours():
    return(data['date/time'].dt.hour)

@st.cache_data(experimental_allow_widgets=True, show_spinner=False)
def get_victim_data(victim_type):
    cols = ['number of ' + victim_type + ' injured','number of ' + victim_type + ' killed']

    victims = data.groupby('on street name').agg({cols[0]:'sum', cols[1]:'sum'})
    victims['Total'] = victims[cols[0]] + victims[cols[1]]
    victims.reset_index(inplace=True)
    victims.rename(
        columns={'on street name':'Street', cols[0]:'Injured', cols[1]:'Died'}, 
        inplace=True
        )
    victims.set_index('Street', inplace=True)
    return(victims.sort_values('Total', ascending=False).head(10))

st.title("New York City Vehicle Collision Analysis")
st.markdown('---')
st.markdown('This web application is built to analyze motor vehicle collisions in NYC using the [New York City Vehicle Collision](%s) data set.' % dataset_link)
st.image("data:image/jpeg;base64,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")
st.sidebar.title('Analyzing the Dataset')
category = st.sidebar.radio("Select category to view", ("Raw Data", "Visualizing with Maps", "Visualizing with charts", "Interactive Data Table", "About Me" ))

if category == "Raw Data":
    st.header("Raw Data")
    st.markdown("Random sample of 20 rows (from 100,000 loaded). Use expand button to the right to view fullscreen.")
    st.write(data.sample(20))

if category == "Visualizing with Maps":
    st.header("Visualizing with Maps")
    st.subheader("2-D Map of Vehicle Collisions by Number of Injuries")
    injured_filter = st.slider("Select minimum number of injuries to filter by", int(0), int(data['number of persons injured'].max()), key='sld_inj')
    st.map(filter_by_injuries(injured_filter))
    st.subheader("Findings:")
    st.markdown("We can observe that the most number of injuries took place at Brownell street I.E 18")
    
    st.markdown('---')

    st.subheader("3-D Map of Vehicle Collisions by Time of Day")
    hour_filter = st.slider("Select hour range to view data on:", 0, 23, (8,18), key='sld_time')
    st.write(filter_by_hour_map(hour_filter))
    st.markdown("From the above interactive slider, we can observe the collisions taken place at a particular time in NewYork City.")

if category == "Visualizing with charts":
    st.header("Visualizing with charts")
    st.subheader("Histogram of Collisions by Time of Day")
    st.plotly_chart(px.histogram(collision_hours(), nbins=24, labels={'value':'Hour of Day (24H)'}).update_layout(bargap=0.05, showlegend=False))
    st.subheader("Key Findings:")
    st.markdown("We can clearly observe that, most of the vehicle collisions takes place in between 2 pm to 5pm, and the least in between 2 am to 5am")
    st.subheader("Recommendations:")
    st.markdown("Increasing more traffic officers during the time in between 2 pm to 5pm. Taking precautionary steps like, maintaining First aid centres near the accident prone zones at this particular time.")

if category == "Interactive Data Table":
    st.header("Interactive Data Table")
    st.subheader("Streets with Highest Frequency of Incidents by Victim Type")
    victim_type = st.selectbox("Victim Type:", ['pedestrians', 'cyclist', 'motorist'])
    st.dataframe(get_victim_data(victim_type), height=450)
    st.subheader("Key Findings:")
    st.write("Broadway street is the dangerous street which tops the list in both pedastrians and cyclists. Also we can see that, the following streets are common in both pedastrians and cyclists: ")
    st.markdown("- Broadway Street")
    st.markdown("- 5 Avenue")
    st.markdown("- 2 Avenue")
    st.markdown("- 7 Avenue")
    st.markdown("Belt Parkway tops when it comes to Motorists with a total of 967 injuries and 4 fatalities")

if category == "About Me":
    st.subheader("My LinkedIn")
    st.markdown("[![My Linkedin](https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg)](https://www.linkedin.com/in/abishek-s-81001/)")

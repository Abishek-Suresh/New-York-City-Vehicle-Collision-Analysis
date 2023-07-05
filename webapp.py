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
st.image("https://miro.medium.com/v2/resize:fill:1200:675/g:fp:0.55:0.7/0*mC7mXxomdLjIOutV")
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

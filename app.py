import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data():
    """Load and clean datasets"""
    forest_data = pd.read_excel('Bird_Monitoring_Data_FOREST.xlsx')
    grassland_data = pd.read_excel('Bird_Monitoring_Data_GRASSLAND.xlsx')

    forest_data.fillna({'Temperature': 0, 'Humidity': 0, 'Initial_Three_Min_Cnt': 0}, inplace=True)
    grassland_data.fillna({'Temperature': 0, 'Humidity': 0, 'Initial_Three_Min_Cnt': 0}, inplace=True)

    forest_data['Location_Type'] = 'Forest'
    grassland_data['Location_Type'] = 'Grassland'

    return forest_data, grassland_data

forest_data, grassland_data = load_data()

combined_data = pd.concat([forest_data, grassland_data], ignore_index=True)

st.sidebar.title("Filters")
location_filter = st.sidebar.selectbox("Select Habitat Type", ["Both", "Forest", "Grassland"])

year_range = combined_data["Year"].unique()
year_range.sort()

start_year, end_year = year_range[0], year_range[-1]

if start_year == end_year:
    st.sidebar.write(f"Year Range: {start_year} (Only one year available)")
    selected_years = (start_year, end_year)
else:
    selected_years = st.sidebar.slider(
        "Select Year Range",
        min_value=start_year,
        max_value=end_year,
        value=(start_year, end_year)
    )

filtered_data = combined_data[
    (combined_data["Year"] >= selected_years[0]) & 
    (combined_data["Year"] <= selected_years[1])
]

if location_filter != "Both":
    filtered_data = filtered_data[filtered_data["Location_Type"] == location_filter]

st.title("Bird Species Observation Dashboard")

st.subheader("Dataset Overview")
st.dataframe(filtered_data)

st.subheader("Top 10 Observed Species")
species_summary = filtered_data.groupby("Common_Name").size().reset_index(name="Observation_Count")
species_summary = species_summary.sort_values("Observation_Count", ascending=False).head(10)

species_chart = px.bar(
    species_summary,
    x="Common_Name",
    y="Observation_Count",
    title="Top 10 Observed Bird Species",
    labels={"Common_Name": "Bird Species", "Observation_Count": "Observation Count"}
)
st.plotly_chart(species_chart)

st.subheader("Environmental Factors Analysis (Temperature vs Humidity)")
if "Temperature" in filtered_data.columns and "Humidity" in filtered_data.columns:
    filtered_data["Initial_Three_Min_Cnt"] = pd.to_numeric(filtered_data["Initial_Three_Min_Cnt"], errors='coerce').fillna(0).astype(int)

    environmental_chart = px.scatter(
        filtered_data,
        x="Temperature",
        y="Humidity",
        color="Location_Type",
        size="Initial_Three_Min_Cnt",
        hover_name="Common_Name",
        title="Temperature vs Humidity vs Bird Count",
        labels={
            "Temperature": "Temperature (°C)",
            "Humidity": "Humidity (%)",
            "Initial_Three_Min_Cnt": "Bird Count"
        }
    )
    st.plotly_chart(environmental_chart)

st.subheader("Observation Trend Over Time")
time_series = filtered_data.groupby(["Year", "Location_Type"]).size().reset_index(name="Observation_Count")

time_series_chart = px.line(
    time_series,
    x="Year",
    y="Observation_Count",
    color="Location_Type",
    title="Bird Observations Over Time",
    labels={"Year": "Year", "Observation_Count": "Observation Count"}
)
st.plotly_chart(time_series_chart)

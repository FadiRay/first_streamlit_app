#import streamlit
#streamlit.title('My Parents New Healthy Diner')


import pandas as pd
import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime, date, timedelta
import datetime as dt

# importing the covid19 data

url        = 'https://opendata.ecdc.europa.eu/covid19/nationalcasedeath_eueea_daily_ei/json'
response_1 = requests.get(url)
covid19    = response_1.json()
df         = pd.DataFrame(pd.DataFrame.from_records(covid19).records.tolist())

#importing the geojson data

geojson_url = 'https://raw.githubusercontent.com/leakyMirror/map-of-europe/master/GeoJSON/europe.geojson'
response_2  = requests.get(geojson_url)
geojson     = response_2.json()

# conn checks is the connection has been successful
def conn():
    return [response_1.status_code, response_2.status_code]

# cleaning the covid19 data 

df = df.dropna()                # deleting na and negative values
df = df[df['cases']>=0]
df = df[df['deaths']>=0]

df = df.astype({'cases': int})  # transforming cases to cases per 100.000
df = df.astype({'deaths': int})
df = df.astype({'popData2020': float})
df['cases'] = df['cases']/df['popData2020']*100000

df['Date'] = pd.to_datetime(df[['year','month','day']])        # making the date as index for easier plotting
df.index   = pd.DatetimeIndex(df['Date'])


df.drop(columns=['dateRep', 'Date', 'day', 'month', 'year', 'countryterritoryCode',
                 'continentExp', 'popData2020'], inplace=True) # deleting extra columns
df.rename(columns={'cases': 'Cases','deaths': 'Deaths',
                   'countriesAndTerritories': 'Country'}, inplace=True)

df_map = df                     # a copy for the map

# start of the dashboarding

st.set_page_config(layout='wide')
st.title('COVID19 DASHBOARDS')

# a radio button widget for choosing the country

country = st.radio(
     'Choose a country:',
      ('Europe', 'Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus',
       'Czechia', 'Denmark', 'Estonia', 'Finland', 'France', 'Germany',
       'Greece', 'Hungary', 'Iceland', 'Ireland', 'Italy', 'Latvia',
       'Liechtenstein', 'Lithuania', 'Luxembourg', 'Malta', 'Netherlands',
       'Norway', 'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia',
       'Spain', 'Sweden'), horizontal=True)  
if country != 'Europe':
    df = df[df['Country']==country]          # filtering the DataFrame by the country

def SelectedCountry():                       # to assert the selected country
    return country==('Europe' or df['Country'][0])

# inserting two side-by-side dashboards

col1, col2 = st.columns(2)
with col1:
    st.header('Cases per 100.000')           # Cases dashboard
    st.line_chart(df['Cases'])
with col2:
    st.header('Deaths')                      # Deaths dashboard
    st.line_chart(df['Deaths'])

# inserting the map dashboard

df_map.rename(columns={'Cases': 'Cases per 100.000'}, inplace=True)

st.header('Covid19 Map in Europe')
col1, col2 = st.columns(2)
with col2:                                   # col2 to select the date and cases/deaths parameter      
    da = st.date_input('Choose a date:', date.today()+timedelta(days=-2))
    
    # checking if the data available for the selected date
    if da > date.today()+timedelta(days=-2):
        st.subheader('No data available yet, latest date:')
        da = date.today()+timedelta(days=-2)
        st.write(da)
    if da < dt.date(2020, 1, 1):
        st.subheader('No data available, earliest date:')
        da = dt.date(2020, 1, 1)
        st.write(da)
    
    parameter = st.radio('',('Cases per 100.000', 'Deaths'))
    
def SelectedParameter():                       # to assert the selected parameter
    return parameter==('Cases per 100.000' or 'Deaths')

df_map.index = df_map.index.astype('str')  
df_map = df_map[df_map.index==str(da)]       # selecting the chosen date

if da > date.today()+timedelta(days=-2):
    st.header('No data available yet')
    da = date.today()+timedelta(days=-2)
    
def SelectedDate():                          # to assert the selected date 
    return da==datetime.date(datetime.strptime(df_map.index[0], '%Y-%m-%d'))

# configuring the map
map_fig = folium.Map(location=[58,18], zoom_start=3)
folium.Choropleth(
    geo_data=geojson,
    data=df_map,
    columns=['geoId', parameter],
    key_on='feature.properties.ISO2',        # this is the key, on which geojson and df_map are connected
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name=parameter).add_to(map_fig)

with col1:
    st_folium(map_fig, height=500, width=700)
    

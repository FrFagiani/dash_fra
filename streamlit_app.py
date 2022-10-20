import streamlit as st
import pandas as pd
import numpy as np
# import geopandas as gpd
# from shapely import wkt
import plotly.express as px
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

st.set_page_config(layout="wide")
st.title('How to visualize and filter dataframe')
st.markdown('Selezionare i dati e visualizzarli in mappa')


def filter_dataframe(df: pd.DataFrame, dfcolsel) -> pd.DataFrame:
    # modify = st.checkbox("Add filters")
    #
    # if not modify:
    #     return df

    df = df.copy()

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filtra il dataframe:", dfcolsel)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Seleziona il range di valori {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Seleziona il range di valori {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Seleziona il range di valori  {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(
                        map(pd.to_datetime, user_date_input)
                    )
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Ricerca stringa o caratteri in {column} (case sensitive)",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df


indices = 'data/Indices_output.csv'
df = pd.read_csv(indices, delimiter=';', encoding='utf-8')

# Columns to filters
df_filtcol = ['Sample',
              'POP',
              'GDP',
              'City',
              'Authority',
              ]
# lanciare la funzione
df = filter_dataframe(df, df_filtcol)
# Select columns to view and to exclude
dfex_col = df.loc[:, df.columns.isin(df_filtcol)]
# Count filtered values
dfcount = str(dfex_col.Sample.count())
# Run in streamlit
st.subheader('Selected cities:'+dfcount)
st.dataframe(dfex_col, height=100)

# df['geometry'] = df['geometry'].apply(wkt.loads)
# gdf = gpd.GeoDataFrame(df, crs='WGS84')
gdf = df

# Select indices to show in map
nofiltcolmap = df_filtcol+(['geometry',
                            'Cont_ID',
                            'DPSVI',
                            'GDPnum',
                            'POPnum'])
filtcolmap = np.setdiff1d(list(df), nofiltcolmap)

option = st.selectbox(
    'Quale indice vuoi visualizzare in mappa?',
    filtcolmap)

gdf = gdf.sort_values(by=[option])

#px.set_mapbox_access_token('pk.eyJ1IjoiZnJmYWdpYW5pIiwiYSI6ImNsOTg2Ynk3ejA1YjMzcm4xOWJ2MDgzOWgifQ.4TX3ZJWRbzz6Y0QKRahadQ')
fig = px.scatter_mapbox(gdf,
                        lat=gdf.lat,
                        lon=gdf.lon,
                        hover_name='City',
                        color=gdf[option].astype('string'),
                        size=option,
                        size_max=15,
                        zoom=3)
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig.update_layout(mapbox_style="open-street-map")

st.plotly_chart(fig, use_container_width=True)

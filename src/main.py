import streamlit as st
import pandas as pd
import numpy as np
from game_fetcher import get_matches_today
import db
import pydeck as pdk
from pydeck.types import String

districts = {
    "Blekinge": 2,
    "Dalsland": 3,
    "Göteborg": 7,
    "Jämtland/Härjedalen": 10,
    "Skåne": 14,
    "Södermanland": 17,
    "Västerbotten": 20,
    "Ångermanland": 23,
    "Bohuslän": 25,
    "Gestrikland": 6,
    "Halland": 8,
    "Medelpad": 11,
    "Småland": 15,
    "Uppland": 18,
    "Västergötland": 21,
    "Örebro län": 13,
    "Gotland": 5,
    "Hälsingland": 9,
    "Norrbotten": 12,
    "Stockholm": 16,
    "Västmanland": 22,
    "Östergötland": 24,
}

st.header("Matcher idag runt om i Sverige")

option = st.selectbox("Välj district", districts.keys())

games = get_matches_today(districts[option])
locations = list(set([g["location"] for g in games]))
cords = db.get_cords(locations)

df = pd.DataFrame(games).reset_index()
df = db.enrich_games_with_cords(df)

df_errors = df[
    (df["longitude"].isna())
    | (df["latitude"].isna())
    | (df["longitude"] == 0.0)
    | (df["latitude"] == 0.0)
]
df = df.drop(df_errors.index)

st.dataframe(df)
st.dataframe(df_errors)

# Create map
avg_lat = df["latitude"].mean()
avg_long = df["longitude"].mean()

st.pydeck_chart(
    pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=avg_lat,
            longitude=avg_long,
            zoom=6,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=df,
                get_position="[longitude, latitude]",
                get_fill_color=[255, 140, 0],
                get_radius=100,
                pickable=True,
                opacity=0.8,
                stroked=True,
                filled=True,
                radius_scale=8,
                radius_min_pixels=4,
                radius_max_pixels=10,
            ),
        ],
        tooltip={
            "text": "{home} - {away} \n {location} \n {competition} \n {timestamp}"
        },
    ),
    use_container_width=True,
)

import streamlit as st
import pandas as pd
import numpy as np
from game_fetcher import get_matches_today
import db
import pydeck as pdk
import math

districts = {
    "Göteborg": 7,
    "Blekinge": 2,
    "Dalsland": 3,
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

with st.expander(f"Matcher med identifierbar plats [{df.shape[0]}]"):
    st.dataframe(df)

with st.expander(f"Matcher med icke identifierbar plats [{df_errors.shape[0]}]"):
    st.dataframe(df_errors)

df["time_formatted"] = pd.to_datetime(df["timestamp"]).dt.strftime("%H:%M")
df["info"] = df.apply(
    lambda row: f"{row['location']} \n {row['home']} - {row['away']} \n {row['competition']} kl {row['time_formatted']}",
    axis=1,
)

df_aggregated = (
    df.groupby(["latitude", "longitude"])
    .agg(
        {
            "info": "\n\n".join,
        }
    )
    .reset_index()
)

location_counts = df.groupby(["latitude", "longitude"]).size().reset_index(name="count")
df_aggregated = pd.merge(
    df_aggregated, location_counts, on=["latitude", "longitude"], how="left"
)

df_aggregated["exits_radius"] = df_aggregated["count"].apply(
    lambda exits_count: math.sqrt(exits_count)
)


print(df_aggregated)

# Create map
avg_lat = df_aggregated["latitude"].mean()
avg_long = df_aggregated["longitude"].mean()

# Modify the layers to include the count as text
st.pydeck_chart(
    pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=avg_lat,
            longitude=avg_long,
            zoom=8,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=df_aggregated,
                get_position="[longitude, latitude]",
                pickable=True,
                stroked=True,
                radius_scale=10,
                radius_min_pixels=4,
                radius_max_pixels=20,
                line_width_min_pixels=1,
                get_radius="count",
                get_fill_color=[34, 139, 34],
            ),
        ],
        tooltip={"text": "{info}"},
    ),
    use_container_width=True,
)

import streamlit as st
import pandas as pd
import numpy as np
from game_fetcher import get_matches_today
import db
import pydeck as pdk
from pydeck.types import String

games = get_matches_today(7)
locations = list(set([g["location"] for g in games]))
cords = db.get_cords(locations)

df = pd.DataFrame.from_dict(cords, orient="index").reset_index()
df = df.rename(columns={"index": "location"})

df = pd.merge(df, pd.DataFrame(games).reset_index(), on="location", how="left")

print(df)


st.pydeck_chart(
    pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=57.708870,
            longitude=11.9745600,
            zoom=11,
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
                radius_scale=2,
                radius_min_pixels=1,
                radius_max_pixels=100,
                line_width_min_pixels=1,
            ),
        ],
        tooltip={
            "text": "{home} - {away} \n {location} \n {competition} \n {timestamp}"
        },
    )
)

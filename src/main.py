import streamlit as st
import pandas as pd
from game_fetcher import get_matches_today
from db import get_cords
import constants
import pydeck as pdk
import math


def fetch_game_data(option):
    return get_matches_today(constants.districts[option])


def fetch_location_coordinates(locations):
    cords = get_cords(locations)
    cords_df = pd.DataFrame.from_dict(cords, orient="index").reset_index()
    cords_df = cords_df.rename(columns={"index": "location"}).reset_index()
    return cords_df


def enrich_game_data_with_coordinates(games_df, cords_df):
    return pd.merge(games_df, cords_df, on="location", how="left")


def filter_and_display_data(games_df):
    # Identify and drop rows with missing or zero coordinates
    df_errors = pd.DataFrame()
    if not "latitude" in games_df.columns or not "longitude" in games_df.columns:
        df_errors = games_df
    else:
        df_errors = games_df[
            (games_df["longitude"].isna())
            | (games_df["latitude"].isna())
            | (games_df["longitude"] == 0.0)
            | (games_df["latitude"] == 0.0)
        ]
    games_df = games_df.drop(df_errors.index)

    # Display expanders with dataframes
    if games_df.shape[0] > 0:
        with st.expander(f"Matcher med identifierbar plats [{games_df.shape[0]}]"):
            games_df_display = games_df.drop(columns=["latitude", "longitude", "index"])
            st.dataframe(games_df_display)

    if df_errors.shape[0] > 0:
        with st.expander(
            f"Matcher med icke identifierbar plats [{df_errors.shape[0]}]"
        ):
            df_errors = df_errors.drop(
                columns=["latitude", "longitude", "index"], errors="ignore"
            )
            st.dataframe(df_errors)

    return games_df


def format_and_enrich_data(games_df):
    # Add formatted time and information columns
    games_df["time_formatted"] = pd.to_datetime(games_df["timestamp"]).dt.strftime(
        "%H:%M"
    )
    games_df["info"] = games_df.apply(
        lambda row: f"{row['location']} \n {row['home']} - {row['away']} \n {row['competition']} kl {row['time_formatted']}",
        axis=1,
    )
    return games_df


def aggregate_location_data(games_df):
    # Aggregate data based on latitude and longitude
    df_aggregated = (
        games_df.groupby(["latitude", "longitude"])
        .agg({"info": "\n\n".join})
        .reset_index()
    )

    # Calculate location counts
    location_counts = (
        games_df.groupby(["latitude", "longitude"]).size().reset_index(name="count")
    )

    # Merge aggregated data with location counts
    df_aggregated = pd.merge(
        df_aggregated, location_counts, on=["latitude", "longitude"], how="left"
    )

    # Calculate exits radius based on counts
    df_aggregated["exits_radius"] = df_aggregated["count"].apply(
        lambda exits_count: math.sqrt(exits_count)
    )

    return df_aggregated


def create_map(df_aggregated):
    # Create map
    avg_lat = df_aggregated["latitude"].mean()
    avg_long = df_aggregated["longitude"].mean()

    # Configure Pydeck layers
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
                    get_fill_color=[0, 71, 171],
                ),
            ],
            tooltip={
                "text": "{info}",
                "style": {
                    "backgroundColor": "rgb(25,25,112)",
                    "color": "white",
                    "font-size": "x-small",
                },
            },
        ),
        use_container_width=True,
    )


def main():
    # Streamlit header
    st.header("Matcher idag")

    # Dropdown to select district
    option = st.selectbox("Välj district", constants.districts.keys())

    # Fetch game data
    games = fetch_game_data(option)

    if len(games) > 0:
        # Fetch location coordinates
        locations = [game["location"].strip() for game in games]
        cords_df = fetch_location_coordinates(locations)

        # Merge game data with location coordinates
        games_df = enrich_game_data_with_coordinates(pd.DataFrame(games), cords_df)

        # Filter and display data
        games_df = filter_and_display_data(games_df)

        if games_df.shape[0] > 0:
            # Format and enrich data
            games_df = format_and_enrich_data(games_df)

            # Aggregate location data
            df_aggregated = aggregate_location_data(games_df)

            # Create and display the map
            create_map(df_aggregated)
    else:
        st.header("Inga matcher idag!")


if __name__ == "__main__":
    main()

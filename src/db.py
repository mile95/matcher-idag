import sqlite3
import os
import pandas as pd
from sqlite_s3_query import sqlite_s3_query


def enrich_games_with_cords(games_df: pd.DataFrame) -> pd.DataFrame:
    locations = games_df["location"].tolist()
    cords = get_cords(locations)
    cords_df = pd.DataFrame.from_dict(cords, orient="index").reset_index()
    cords_df = cords_df.rename(columns={"index": "location"}).reset_index()

    res = pd.merge(games_df, cords_df, on="location", how="left")
    res = res.rename(columns={"index": "location"}).reset_index()
    # TODO: This merge can probably be improved so that the drops are not needed
    res = res.drop("index_x", axis=1)
    res = res.drop("index_y", axis=1)
    res = res.drop("index", axis=1)
    return res


def get_cords(locations: list[str]):
    with sqlite_s3_query(
        url="https://matcher-idag-locations.s3.eu-central-1.amazonaws.com/db.db"
    ) as query:
        params = tuple(locations)
        with query(
            f"SELECT name, latitude, longitude FROM locations WHERE name IN {params}"
        ) as (columns, rows):
            result = {}
            for row in rows:
                name, latitude, longitude = row
                if latitude is not None and longitude is not None:
                    result[name] = {
                        "latitude": float(latitude),
                        "longitude": float(longitude),
                    }
                else:
                    result[name] = {"latitude": float(0), "longitude": float(0)}

            return result

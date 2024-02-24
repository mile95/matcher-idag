import sqlite3
import os
import pandas as pd

DATABASE_PATH = os.path.join("data/db.db")


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
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT name, latitude, longitude FROM locations
        WHERE name IN ({})
    """.format(
            ",".join(["?"] * len(locations))
        ),
        locations,
    )

    rows = cursor.fetchall()

    result = {}
    for row in rows:
        name, latitude, longitude = row
        if latitude is not None and longitude is not None:
            result[name] = {"latitude": float(latitude), "longitude": float(longitude)}
        else:
            result[name] = {"latitude": float(0), "longitude": float(0)}

    conn.close()

    return result

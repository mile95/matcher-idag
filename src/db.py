import sqlite3
import os

DATABASE_PATH = os.path.join("data/db.db")


def get_cords(locations: list[str]) -> dict:
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

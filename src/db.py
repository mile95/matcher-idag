import sqlite3
import os

DATABASE_PATH = os.path.join("../data/db.db")
print(DATABASE_PATH)


def get_cords(locations: list[str]):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Use a single query with WHERE IN clause
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
        # TODO: Handle if not found

    # Close the database connection
    conn.close()

    return result

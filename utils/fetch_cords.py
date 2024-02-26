from selenium import webdriver
from selenium.webdriver.common.by import By
import sqlite3
import sys


def insert_data_to_db(data):
    conn = sqlite3.connect("../data/db.db")
    cursor = conn.cursor()

    for location, coordinates in data.items():
        cursor.execute(
            """
            INSERT OR IGNORE INTO locations (name, latitude, longitude)
            VALUES (?, ?, ?)
        """,
            (location, coordinates[0], coordinates[1]),
        )

    conn.commit()
    conn.close()


def main(facility_id: int):
    driver = webdriver.Chrome()
    url = f"https://www.gbgfotboll.se/rs/anlaggning/xl/{facility_id}/"
    d = {}
    try:
        driver.get(url)
        google_maps_link = driver.find_element(
            By.XPATH, '//a[@class="facility__map-link"]'
        )
        google_maps_url = google_maps_link.get_attribute("href")
        if google_maps_url:
            long, lat = google_maps_url.split("=")[1].split(",")
            header = driver.find_element(
                By.XPATH,
                '//h1[@class="headline headline--tight headline--xlarge headline--light"]',
            )
            if header:
                d[header.text] = [long, lat]
    except Exception as e:
        print(f"failed for {facility_id}")

    if d:
        print(d)
        insert_data_to_db(d)
    driver.quit()

    print(f"done for {facility_id}")


if __name__ == "__main__":
    facility_id = sys.argv[1]
    main(facility_id)

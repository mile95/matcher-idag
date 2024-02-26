# Matcher Idag

https://matcher-idag.streamlit.app/

Application that displays today's football games around Sweden on a map.

## Running locally

    pip3 install -r requirements.txt
    streamlit run src/main.py

## Updating location database

I have not found any API for getting the coordinates for a given venue/facility.

To solve this, I created the `utils/fetch_cords.py` script which uses `selenium` to fetch the coordinates for a given facility.

Identifying games at a facility with unknown coordinates and fetching those is today a manual process since it requires selenium (a web driver) to fetch and store the coordinates.

To add a facility with coordinates to the `db`, run

    pip3 install -r requirements_dev.txt
    python3 fetch_cords.py <facility_id>


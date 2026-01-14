# ViennaNext - Technical Deep Dive

This document explains **how everything works** under the hood, from the raw data processing to the final user interface.

## 1. Architecture Overview

ViennaNext is a **Python Flask** web application that acts as a bridge between the user and the **Wiener Linien Realtime API**.

*   **Backend**: Python (Flask) handles routing, database interactions, and API proxying.
*   **Database**: SQLite (`app.db`) stores user accounts and favourites.
*   **Frontend**: HTML/CSS/JS uses `fetch()` to get data from the backend and renders it dynamically.
*   **Data Source**: Official Wiener Linien Open Government Data (CSV) and Realtime API (JSON).

---

## 2. The Data Challenge: "How do we find the stations?"

The biggest challenge was getting a list of all stations and their correct IDs. The Wiener Linien API requires a specific **RBL ID** (Rechnergesteuertes Betriebsleitsystem) to get departure times. A single station name like "Stephansplatz" isn't enough; we need the specific RBL IDs for the platforms.

### How `import_data.py` works

I wrote a script (`import_data.py`) to automate this:

1.  **Download CSVs**: It downloads three official datasets from `data.wien.gv.at`:
    *   `wienerlinien-ogd-haltestellen.csv`: List of all station names and IDs.
    *   `wienerlinien-ogd-linien.csv`: List of all lines (U-Bahn, Tram, Bus).
    *   `wienerlinien-ogd-steige.csv`: The "glue" file. It links Stations + Lines to **RBL IDs**.

2.  **Filtering**:
    *   It filters `linien` to only keep those with `ECHTZEIT=1` (Realtime capable).
    *   It maps Line IDs to names (e.g., "U1", "13A").

3.  **Grouping (The Magic Step)**:
    *   The script iterates through the `steige` (platforms) file.
    *   It groups **RBL IDs** by their Station Name and Line.
    *   *Example*: "Stephansplatz" + "U3" might have two RBL IDs: `4906` (towards Ottakring) and `4911` (towards Simmering).
    *   The script combines these into a single entry: `{'id': '4906,4911', 'name': 'Stephansplatz (U3)'}`.

4.  **Encoding**:
    *   The script forces `utf-8` encoding to ensure characters like "ß" and "ä" are displayed correctly.

5.  **Output**:
    *   It generates `stops_data.py`, a Python file containing a massive list of ~2,800 verified stops. This file is imported by the main app.

---

## 3. The Backend (`app.py` & `wienerlinien.py`)

### The API Wrapper (`wienerlinien.py`)
When you search for a stop, the backend calls `get_departures(stop_id)`.
*   **Multiple IDs**: Since our `stops_data.py` contains comma-separated IDs (e.g., "4906,4911"), the wrapper splits them up.
*   **API Request**: It sends a request to `http://www.wienerlinien.at/ogd_realtime/monitor` with multiple `rbl` parameters:
    `?rbl=4906&rbl=4911&activateTrafficInfo=stoerungkurz`
*   **Parsing**: It loops through the complex JSON response, extracting the Line Name, Direction, and Countdown time for every monitor.

### The Database (`db.py`)
We use **SQLite** for simplicity.
*   **Users Table**: Stores `username` and `password` (hashed/plaintext for this demo).
*   **Favourites Table**: Links `user_id` to a `stop_id` and `stop_name`.
*   **Logic**: When you click "Add to Favourites", it saves the ID pair (e.g., "4906,4911") so we can load both directions later.

---

## 4. The Frontend (`dashboard.html` & `script.js`)

### Search Bar (Select2)
I used the **Select2** library to create the search experience.
*   It turns a standard HTML `<select>` box into a searchable, scrollable dropdown.
*   It loads the 2,800+ options generated in `dashboard.html` (passed from `stops_data.py`).

### Dynamic Updates
1.  **Selection**: When you pick a station, `script.js` gets the ID (e.g., "4906,4911").
2.  **Fetch**: It calls our internal API `/api/departures?stop_id=4906,4911`.
3.  **Rendering**: The backend returns a clean JSON list of departures. The JavaScript then:
    *   Clears the table.
    *   Loops through the departures and creates HTML table rows `<tr>`.
    *   Populates the "Filter by Direction" dropdown based on the unique directions found in the response.

### Filtering & Pagination
*   **Filtering**: The "Filter by Direction" dropdown works entirely in the browser (Client-side). It hides rows that don't match the selected direction.
*   **Pagination**: We maintain a variable `itemsToShow` (default 10). Clicking "Show More" increases this limit and re-renders the table.

---

## Summary of Flow

1.  **Import**: `import_data.py` reads CSVs -> creates `stops_data.py`.
2.  **Startup**: `app.py` loads `stops_data.py`.
3.  **User**: Selects "Stephansplatz (U3)" in the UI.
4.  **Frontend**: Sends ID "4906,4911" to Backend.
5.  **Backend**: Calls Wiener Linien API with `rbl=4906` AND `rbl=4911`.
6.  **API**: Returns data for both directions.
7.  **Backend**: Processes JSON -> Returns simplified list to Frontend.
8.  **Frontend**: Renders table, enables filtering.

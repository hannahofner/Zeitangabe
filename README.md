# ViennaNext 🚇

A simple educational Python web app to display real-time Vienna public transport departures.

## Setup & Installation

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Initialize Database**:
    The database (`app.db`) is automatically created when you run the app for the first time.
    You can also manually initialize it by running:
    ```bash
    python db.py
    ```

3.  **Run the Application**:
    ```bash
    python app.py
    ```
    The app will start at `http://127.0.0.1:5000`.

## Usage

1.  **Register**: Create a new account on the home page.
2.  **Login**: Log in with your credentials.
3.  **Search**:
    - Enter a Stop (e.g. Stephansplatz).
    - Or click one of the example buttons.
4.  **Favourites**:
    - Click "Add to Favourites" after searching for a stop.
    - View your favourites in the "My Favourites" list.
    - Click a favourite to quickly load its departures.



## Tech Stack

- **Backend**: Python, Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS, Vanilla JavaScript
- **API**: Wiener Linien Monitor API

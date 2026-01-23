# Bioskin_GDP

# Bioskin Mixed Sensor Dashboard

A real-time visualization dashboard designed to monitor biosensor data from a smart glove or prosthetic hand. This application fetches live data from a Google Sheet and visualizes Temperature, Capacitive Force, and Resistive Force on a mapped hand topology.

## Features
- **Live Monitoring:** Fetches sensor data every 2 seconds from a Google Sheet CSV feed.
- **Hand Topology Map:** Visualizes sensor locations (Index Finger, Middle Finger, etc.) on a coordinate-mapped hand outline.
- **Anti-Jitter Logic:** Includes a safety buffer (Session State) to ignore "stale" data if Google Servers return cached/old rows.
- **Smart Buffering:** Reads the last 50 rows of history to ensure no finger data is missed during batch uploads.
- **Data Export:** Built-in tool to convert the full sensor history into a downloadable Excel (.xlsx) file.
- **Debug Mode:** View raw incoming dataframes to troubleshoot connection issues.

## Prerequisites
- Python 3.8 or higher
- Internet connection (to fetch Google Sheets data)

## Dependencies
This project requires the following Python libraries:
- streamlit
- plotly
- pandas
- numpy
- openpyxl

## Installation
1. Clone this repository or download the source code.
2. Install the required dependencies:
   pip install streamlit plotly pandas numpy openpyxl

## Configuration
The application reads from a public Google Sheet CSV link defined in `app.py`.

To use your own data:
1. Open your Google Sheet.
2. Go to File > Share > Publish to web.
3. Select "Entire Document" and "Comma-separated values (.csv)".
4. Paste the generated link into `app.py` at the variable `BASE_SHEET_URL`.

## Usage
1. Open your terminal/command prompt.
2. Navigate to the project directory.
3. Run the application:
   streamlit run app.py

The dashboard will open automatically in your web browser at http://localhost:8501.

## Troubleshooting
- **Dashboard not updating?**
  Google Sheets "Publish to Web" has a natural delay of 3-5 minutes. If the "Last Fetch" time is updating but values aren't, wait for the Google cache to refresh.
- **Charts stuck on old data?**
  If you cleared your Google Sheet rows, the dashboard might think the new data is a "glitch" because the row numbers are lower. Click the "Reset / Unfreeze" button in the sidebar to clear the dashboard's memory.

## Security Note
This repository connects to a Google Sheet via a public CSV link.
DO NOT upload/commit any "service_account.json" files or private API keys to this repository. All authentication should be handled locally or via environment variables.

## License
[Your License Here, e.g., MIT License]

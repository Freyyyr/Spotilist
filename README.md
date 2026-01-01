# Spotilist 🎵

Spotilist is a Streamlit-based Python application designed to export your Spotify playlists into CSV files. It automatically fetches track metadata (artists, album, release date, etc.) and packages everything into a convenient downloadable ZIP file.


## Prerequisites

- **Python 3.9+** installed.
- A **Spotify Developer Account** to obtain API credentials.

## Installation

1. **Clone the repository and navigate to the folder.**

2. **Create a virtual environment (Recommended):**
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:
```Bash
pip install -r requirements.txt
```

## Configuration

This application requires Spotify API credentials to access your playlists.

    1. Go to the Spotify Developer Dashboard.
    2. Create a new app to obtain your Client ID and Client Secret.
    3. In your app settings on the dashboard, add the following URL to the Redirect URIs whitelist:

        http://localhost:8080 (or the port defined in your script)

First Run Setup: Upon launching the application for the first time, you will be prompted to enter your credentials directly in the interface:

    - SPOTIPY_CLIENT_ID
    - SPOTIPY_CLIENT_SECRET
    - SPOTIPY_REDIRECT_URI

These will be saved locally in a .env file for future use.

## Running Locally

To start the application in development mode:
Bash

streamlit run app/script.py

## Building the Executable

To compile the application into a standalone executable file using PyInstaller:
Bash

### Windows / Linux / macOS
pyinstaller Spotilist.spec --clean

Ensure that your Spotilist.spec file is correctly configured to include the Streamlit runtime hooks and datas.


## ⚠️ Important Note for Executable Users

**Please read before using the `.exe` version:**

Since Streamlit acts as a local web server, closing the browser window **does not** stop the application process running in the background.

To close the application properly and release the network port:
**You must click the "Quit" button located in the sidebar.**

*If you do not use this button, the background process will remain active, which may prevent the application from restarting correctly (causing "Port already in use" errors).*

---
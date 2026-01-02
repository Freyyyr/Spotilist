# Spotilist 🎵

Spotilist is a cross-platform desktop application (Electron + Python/Streamlit) designed to export your Spotify playlists into CSV files. It automatically fetches track metadata (artists, album, release date, etc.) and packages everything into a convenient downloadable ZIP file.

## Project Structure

The project is divided into two main parts:

    backend/: Contains the Python source code (Streamlit app & logic).

    main.js & Root: Contains the Electron configuration to wrap the Python backend into a desktop executable.

## Prerequisites

- Python 3.9+ installed.
- Node.js and npm installed (for building the desktop app).
- A Spotify Developer Account to obtain API credentials.

### Spotify Developer Account
This application requires Spotify API credentials to access your playlists.

1. Go to the Spotify Developer Dashboard.
2. Create a new app to obtain your Client ID and Client Secret.
3. In your app settings on the dashboard, add the following URL to the Redirect URIs whitelist: http://localhost:8080

## Running Locally

### Setup

You first need to install the python and npm packages.
### Run the python app

If you just want to test the application features/UI without building the full executable:
```Bash
streamlit run backend/app.py
```

Note: This runs in your browser, like a standard web app.

### Building the electron app

Run the command corresponding to your OS:
```Bash
# Linux
npm run build:linux
# Windows
npm run build:win
# macOS
npm run build:mac
```

### Notes

Yser's data will be saved locally in the application's user data folder:

    Windows: %APPDATA%/Spotilist/

    Linux: ~/.config/Spotilist/

    macOS: ~/Library/Application Support/Spotilist/

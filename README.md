# Spotilist 🎵

Spotilist is a Python application built with Streamlit that allows you to export your Spotify playlists into CSV files. It fetches track metadata (artists, album, release date, etc.) and packages everything into a downloadable ZIP file.

## 📋 Prerequisites

- **Python 3.9+** installed.
- A **Spotify Developer Account** to get API credentials.

## ⚙️ Installation

Create a virtual environment (Recommended)

Install dependencies:
```
pip install -r requirements.txt
```

## Configuration (.env)

This application requires Spotify API credentials. You must create a .env file in the root directory.

Go to the Spotify Developer Dashboard.

Create an app and get your Client ID and Client Secret.

Add <REDIRECT_URI> to the Redirect URIs in your Spotify app settings.

Create a .env file with the following content:

```
SPOTIPY_CLIENT_ID=your_client_id_here
SPOTIPY_CLIENT_SECRET=your_client_secret_here
SPOTIPY_REDIRECT_URI=REDIRECT_URI
```

## Running Locally

To start the application in development mode:
```
streamlit run app/script.py
```

## Building the Executable (PyInstaller)

### Build Command

Run the build process using the verified .spec file:
```
# Windows / Linux / macOS
pyinstaller Spotilist.spec --clean
```

### Distribution

The executable will be generated in the dist/ folder.

⚠️ IMPORTANT: The executable does not contain your .env file. When you share the app, you must provide the executable AND ask the user to create their own .env file in the same folder.

Folder content for distribution:
```
/My_Release_Folder
  ├── Spotilist.exe  (or 'Spotilist' on Linux)
  └── .env           (User must fill this)
```
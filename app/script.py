import streamlit as st
from spotipy import oauth2, Spotify
import os
import pandas as pd
from dotenv import load_dotenv
import io
import zipfile
import traceback
import time

st.set_page_config(page_title="Spotilist", page_icon="🎵", layout="wide")

load_dotenv()

# --- CONSTANTES ---
SCOPE = "playlist-read-private"
CACHE = ".spotipyoauthcache"
ENV_FILE = ".env"

# --- FONCTIONS UTILITAIRES ---

def check_credentials():
    """Vérifie si les clés nécessaires sont présentes dans l'environnement."""
    return all([
        os.getenv("SPOTIPY_CLIENT_ID"),
        os.getenv("SPOTIPY_CLIENT_SECRET"),
        os.getenv("SPOTIPY_REDIRECT_URI")
    ])

def save_credentials(client_id, client_secret, redirect_uri):
    """Ecrit les identifiants dans un fichier .env."""
    with open(ENV_FILE, "w") as f:
        f.write(f'SPOTIPY_CLIENT_ID="{client_id}"\n')
        f.write(f'SPOTIPY_CLIENT_SECRET="{client_secret}"\n')
        f.write(f'SPOTIPY_REDIRECT_URI="{redirect_uri}"\n')

def get_auth():
    auth_manager = oauth2.SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope=SCOPE,
        cache_path=CACHE,
    )
    return Spotify(auth_manager=auth_manager)

def process_track(track_item):
    if track_item["track"] is None or track_item["track"]["is_local"]:
        return None

    t = track_item["track"].copy()
    
    artist_names = ", ".join([artist["name"] for artist in t["artists"]])
    
    clean_track = {
        "id": t["id"],
        "artists": artist_names,
        "name": t["name"],
        "album_name": t["album"]["name"],
        "added_at": track_item["added_at"],
        "album_type": t["album"]["album_type"],
        "album_release_date": t["album"]["release_date"],
        "duration_ms": t["duration_ms"],
        "href": t["href"],
        "spotify_url": t["external_urls"]["spotify"]
    }
    return clean_track

def get_playlist_data(sp, playlist_id):
    try:
        results = sp.playlist_tracks(playlist_id)
        tracks = results["items"]
        
        while results["next"]:
            results = sp.next(results)
            tracks.extend(results["items"])
        
        clean_tracks = []
        errors = 0
        
        for item in tracks:
            processed = process_track(item)
            if processed:
                clean_tracks.append(processed)
            else:
                errors += 1
                
        if clean_tracks:
            df = pd.DataFrame(clean_tracks)
            return df, errors
        return None, errors
    except Exception as e:
        st.error(f"Error fetching playlist: {e}")
        return None, 0

# --- UI LOGIC ---

st.title("🎵 Spotilist")

with st.sidebar:
    st.divider()
    if st.button("Quit", type="primary"):
        st.warning("Closing the app...")
        time.sleep(1)
        os._exit(0)

if not check_credentials():
    st.warning("Missing configuration. Please entrer your Spotify API keys.")
    st.markdown("You can obtain it from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).")
    
    with st.form("credentials_form"):
        client_id = st.text_input("Client ID", type="password")
        client_secret = st.text_input("Client Secret", type="password")
        redirect_uri = st.text_input("Redirect URI", value="http://127.0.0.1:8080")
        
        submitted = st.form_submit_button("Save and start")
        
        if submitted:
            if client_id and client_secret and redirect_uri:
                save_credentials(client_id, client_secret, redirect_uri)
                st.success("Configuration saved ! Reloading...")
                st.rerun()
            else:
                st.error("Please fill all fields.")
    
    st.stop()


st.markdown("A spotify playlist exporter.")

if 'sp' not in st.session_state:
    try:
        sp = get_auth()
        user = sp.current_user()
        st.session_state['sp'] = sp
        st.session_state['user'] = user
        st.success(f"Connected as **{user['display_name']}**")
    except Exception as e:
        st.error("Authentification failure. Your keys might be invalid.")
        if st.button("Reset configuration"):
            if os.path.exists(ENV_FILE):
                os.remove(ENV_FILE)
            if os.path.exists(CACHE):
                os.remove(CACHE)

            keys_to_remove = ["SPOTIPY_CLIENT_ID", "SPOTIPY_CLIENT_SECRET", "SPOTIPY_REDIRECT_URI"]
            for key in keys_to_remove:
                if key in os.environ:
                    del os.environ[key]
            st.rerun()
        st.stop()

if 'sp' in st.session_state:
    sp = st.session_state['sp']
    user_id = st.session_state['user']['id']

    if st.button("🔍 Fetch my playlists"):
        with st.spinner("Retrieving playlist list..."):
            playlists = []
            try:
                results = sp.user_playlists(user_id)
                playlists.extend(results["items"])
                
                while results["next"]:
                    results = sp.next(results)
                    playlists.extend(results["items"])
                
                st.session_state['playlists'] = playlists
                st.success(f"{len(playlists)} playlists found!")
            except Exception as e:
                st.error(f"Error fetching playlists: {e}")

    if 'playlists' in st.session_state:
        playlists = st.session_state['playlists']
        
        st.subheader("Export Data")
        
        playlist_options = {p['name']: p['id'] for p in playlists}
        selected_playlists = st.multiselect(
            "Which playlists do you want to export?", 
            options=playlist_options.keys(),
            default=list(playlist_options.keys())[:1]
        )

        if st.button("Start Extraction") and selected_playlists:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                total = len(selected_playlists)
                
                for i, p_name in enumerate(selected_playlists):
                    p_id = playlist_options[p_name]
                    status_text.text(f"Processing: {p_name}...")
                    
                    df, errors = get_playlist_data(sp, p_id)
                    
                    if df is not None:
                        safe_name = "".join([c for c in p_name if c.isalnum() or c in (' ', '-', '_')]).strip()
                        if not safe_name: safe_name = "playlist"
                        
                        csv_data = df.to_csv(index=False).encode('utf-8')
                        zf.writestr(f"{safe_name}.csv", csv_data)
                    
                    progress_bar.progress((i + 1) / total)

            progress_bar.progress(100)
            status_text.text("Done!")
            
            st.download_button(
                label="📥 Download all playlists (ZIP)",
                data=zip_buffer.getvalue(),
                file_name="my_spotify_playlists.zip",
                mime="application/zip"
            )
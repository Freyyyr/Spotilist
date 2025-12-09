import streamlit as st
from spotipy import oauth2, Spotify
import os
import pandas as pd
from dotenv import load_dotenv
import io
import zipfile

load_dotenv()

st.set_page_config(page_title="Spotilist", page_icon="🎵", layout="wide")

SCOPE = "playlist-read-private"
CACHE = ".spotipyoauthcache"

def get_auth():
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

    if not client_id or not client_secret:
        st.error("⚠️ API keys missing in .env file")
        return None

    auth_manager = oauth2.SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
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
    results = sp.playlist_tracks(playlist_id)
    tracks = results["items"]
    
    # Handle pagination to get all tracks
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


# --- UI Starts Here ---

st.title("🎵 Spotilist")
st.markdown("A spotify playlist exporter.")


# Authentication
if 'sp' not in st.session_state:
    sp = get_auth()
    if sp:
        try:
            user = sp.current_user()
            st.session_state['sp'] = sp
            st.session_state['user'] = user
            st.success(f"Connected as **{user['display_name']}**")
        except Exception as e:
            st.warning("Please authenticate in the pop-up window or check your API keys.")
            st.stop()

if 'sp' in st.session_state:
    sp = st.session_state['sp']
    user_id = st.session_state['user']['id']

    if st.button("🔍 Fetch my playlists"):
        with st.spinner("Retrieving playlist list..."):
            playlists = []
            results = sp.user_playlists(user_id)
            playlists.extend(results["items"])
            
            while results["next"]:
                results = sp.next(results)
                playlists.extend(results["items"])
            
            st.session_state['playlists'] = playlists
            st.success(f"{len(playlists)} playlists found!")

    if 'playlists' in st.session_state:
        playlists = st.session_state['playlists']
        
        st.subheader("Export Data")
        
        playlist_options = {p['name']: p['id'] for p in playlists}
        selected_playlists = st.multiselect(
            "Which playlists do you want to export?", 
            options=playlist_options.keys(),
            default=playlist_options.keys()
        )

        if st.button("🚀 Start Extraction"):
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
                        safe_name = "".join([c for c in p_name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
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
            
            if 'df' in locals() and df is not None:
                st.write("Preview of the last processed playlist:")
                st.dataframe(df.head())
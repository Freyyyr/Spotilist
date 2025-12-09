from spotipy import oauth2, Spotify
import os
import shutil
import sys
import pandas as pd
from pandas import json_normalize
from dotenv import load_dotenv

load_dotenv()

SCOPE = "playlist-read-private"
CACHE = ".spotipyoauthcache"

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8080") 

def create_spotify():
    if not SPOTIPY_CLIENT_ID or not SPOTIPY_CLIENT_SECRET:
        print("Clés API manquantes dans le fichier .env")
        return None
    
    auth_mg = oauth2.SpotifyOAuth(
        SPOTIPY_CLIENT_ID,
        SPOTIPY_CLIENT_SECRET,
        SPOTIPY_REDIRECT_URI,
        scope=SCOPE,
        cache_path=CACHE,
    )
    spotify = Spotify(auth_manager=auth_mg)
    return spotify, auth_mg


def call_playlist(user, playlist_id, sp):
    errors = 0
    results = sp.user_playlist_tracks(user, playlist_id)
    playlist = results["items"]  
    track_list = []
    k = 0
    for i in range(len(playlist)):
        if playlist[i]["track"] is not None:
            if playlist[i]["track"]["is_local"] is False:
                track_list.append(playlist[i]["track"].copy())
                track_list[k].pop("preview_url")
                track_list[k].pop("available_markets")
                track_list[k].pop("explicit")
                track_list[k].pop("uri")
                track_list[k].pop("is_local")
                track_list[k].pop("popularity")
                track_list[k].pop("external_ids")
                track_list[k].pop("track")
                track_list[k].pop("type")
                track_list[k].pop("album")
                track_list[k].pop("episode")
                
                track_list[k]["artists"] = ", ".join([playlist[i]["track"]["artists"][j]["name"] for j in range(len(playlist[i]["track"]["artists"]))])
                track_list[k]["added_at"] = playlist[i]["added_at"]
                track_list[k]["album_name"] = playlist[i]["track"]["album"]["name"]
                track_list[k]["album_type"] = playlist[i]["track"]["album"]["album_type"]
                track_list[k]["album_release_date"] = playlist[i]["track"]["album"]["release_date"]
            
            else:
                track_list.append({})
                track_list[k]["artists"] = playlist[i]["track"]["artists"][0]["name"]
                track_list[k]["name"] = playlist[i]["track"]["name"]
                track_list[k]["album"] = playlist[i]["track"]["album"]
            k += 1
        else:
            errors += 1
            
    track_list = json_normalize(track_list)
    playlist_df = pd.DataFrame.from_dict(track_list)
    
    while results["next"]:
        results = sp.next(results)
        playlist = results["items"]
        track_list = []
        k = 0
        for i in range(len(playlist)):
            if playlist[i]["track"] is not None:
                if playlist[i]["track"]["is_local"] is False:
                    track_list.append(playlist[i]["track"].copy())
                    track_list[k].pop("preview_url")
                    track_list[k].pop("available_markets")
                    track_list[k].pop("explicit")
                    track_list[k].pop("uri")
                    track_list[k].pop("is_local")
                    track_list[k].pop("popularity")
                    track_list[k].pop("external_ids")
                    track_list[k].pop("track")
                    track_list[k].pop("type")
                    track_list[k].pop("album")
                    track_list[k].pop("episode")
                    
                    track_list[k]["artists"] = ", ".join([playlist[i]["track"]["artists"][j]["name"] for j in range(len(playlist[i]["track"]["artists"]))])
                    track_list[k]["added_at"] = playlist[i]["added_at"]
                    track_list[k]["album_name"] = playlist[i]["track"]["album"]["name"]
                    track_list[k]["album_type"] = playlist[i]["track"]["album"]["album_type"]
                    track_list[k]["album_release_date"] = playlist[i]["track"]["album"]["release_date"]
                
                else:
                    track_list.append({})
                    track_list[k]["artists"] = playlist[i]["track"]["artists"][0]["name"]
                    track_list[k]["name"] = playlist[i]["track"]["name"]
                    track_list[k]["album"] = playlist[i]["track"]["album"]
                k += 1
            else:
                errors += 1
            
        track_list = json_normalize(track_list)
        track_df = pd.DataFrame.from_dict(track_list)
        playlist_df = pd.concat([playlist_df, track_df], ignore_index=True)

    if not playlist_df.empty:
        playlist_df = playlist_df[["id", "artists", "name", "album_name", "added_at", "album_type", "album_release_date", "duration_ms", "href", "external_urls.spotify"]]
        return playlist_df, errors
    else:
        return None, 0


def get_all_playlist(user, sp, path):
    print("Recherche des playlists...")
    try:
        results = sp.user_playlists(user)
    except Exception as error:
        print("Utilisateur introuvable.")
        return
    
    pl_data = results["items"]
    playlists = []
    for pl in pl_data:
        playlists.append({"name": pl["name"], "id": pl["id"]})
    while results["next"]:
        results = sp.next(results)
        pl_data = results["items"]
        for pl in pl_data:
            playlists.append({"name": pl["name"], "id": pl["id"]})
    print(str(len(playlists)) + " playlists trouvées")
    
    print("***************************")
    print("Récuperation des playlists.")
    i = 1
    for pl in playlists:
        print("Playlist : " + pl["name"])
        data, errors = call_playlist(user, pl["id"], sp)
        if data is not None:
            data.to_csv(f"{path}{i}_{user}_{pl['name'].replace('/', '')}_{pl['id']}.csv", index=True)
            print("Récupération de " + pl["name"] + " : OK. " + str(errors) + " erreurs.")
        else:
            print("Récupération de " + pl["name"] + " : Playlist vide.")
        i = i + 1
    print(f"{i} playlists récupérées et exportées dans le dossier /data/.")


print("Connexion à l'API Spotify...")
path = "~/Documents/playlists/"
absolute_path = os.path.expanduser(path)

if os.path.exists(absolute_path):
    shutil.rmtree(absolute_path)

os.makedirs(absolute_path)
if create_spotify() is None: 
    sys.exit()
sp, auth_code = create_spotify()
user_profile = sp.current_user()
username = user_profile['id']
get_all_playlist(username, sp, path)
print("Fin.")
print("Appuyer sur une touche pour fermer")
x = input()
sys.exit()

import os, sys, io, time, zipfile, traceback
import streamlit.web.cli as stcli
import streamlit as st
import pandas as pd

from spotipy import oauth2, Spotify
from dotenv import load_dotenv


def resolve_path(path):
    if getattr(sys, "frozen", False):
        basedir = sys._MEIPASS
    else:
        basedir = os.path.dirname(__file__)
    return os.path.join(basedir, path)

if __name__ == "__main__": 
    filename = resolve_path("script.py")
    
    sys.argv = [
        "streamlit",
        "run",
        filename,
        "--global.developmentMode=false",
        "--server.headless=true",
        "--server.address=127.0.0.1",
        "--server.port=8501",
        "--server.fileWatcherType=none"
    ]
    sys.exit(stcli.main())
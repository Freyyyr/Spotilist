import sys
import os
from streamlit.web import cli as stcli

def main():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)

    script_path = os.path.join(base_path, "app", "script.py")

    sys.argv = ["streamlit", "run", script_path, "--global.developmentMode=false"]
    
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()
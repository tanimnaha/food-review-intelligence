# Entrypoint redirect for Streamlit Community Cloud
from pathlib import Path
import runpy

app_path = Path(__file__).resolve().parent / "streamlit_app" / "app.py"
runpy.run_path(str(app_path), run_name="__main__")

"""Source-checkout compatibility entry point for the installed renderer."""
import runpy
from pathlib import Path
if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parents[1] / "github/scripts/render_social_preview.py"), run_name="__main__")

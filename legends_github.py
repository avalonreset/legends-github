#!/usr/bin/env python3
"""Agent-neutral entry point for the existing Legends GitHub command runtime."""
from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parent / "github" / "scripts" / "run_headless.py"), run_name="__main__")

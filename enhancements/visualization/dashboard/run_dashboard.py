"""
Script to run the RME Dashboard.
"""

import os
import subprocess
import sys
import webbrowser
from time import sleep

def run_dashboard():
    """Run the Streamlit dashboard."""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the script directory
    os.chdir(script_dir)
    
    # Open the dashboard in the default web browser after a short delay
    def open_browser():
        sleep(2)  # Wait for Streamlit to start
        webbrowser.open('http://localhost:8501')
    
    # Start the browser in a separate thread
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run the Streamlit app
    try:
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'app.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running dashboard: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nDashboard stopped by user.")
        sys.exit(0)

if __name__ == "__main__":
    run_dashboard() 
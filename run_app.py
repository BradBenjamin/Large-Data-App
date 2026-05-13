import subprocess
import sys
import os
import time

def main():
    # 1. Find exactly where run_app.py is located on your computer
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Force Python to make this folder the "Current Working Directory"
    os.chdir(base_dir)
    
    # 3. Now the relative paths will work perfectly every time
    app_path = os.path.join("app", "app.py")

    print("🚀 Starting the Machine Learning Backend (FastAPI)...")
    
    # We add cwd=base_dir just as an extra layer of safety
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=base_dir
    )

    # Give the backend a second to boot up
    time.sleep(2)

    print("🎨 Starting the Frontend UI (Streamlit)...")
    ui_process = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.address=0.0.0.0",
            "--server.port=8501",
            "--server.enableCORS=false"
        ],
        cwd=base_dir
    )

    try:
        # Keep the main script alive
        api_process.wait()
        ui_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        api_process.terminate()
        ui_process.terminate()
        sys.exit(0)

if __name__ == "__main__":
    main()

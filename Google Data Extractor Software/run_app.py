#!/usr/bin/env python3
"""
Google Maps Data Extractor - Startup Script

This script starts the FastAPI server and opens the web interface in the default browser.
"""

import subprocess
import sys
import time
import webbrowser
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import selenium
        import pandas
        import webdriver_manager
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def check_chrome():
    """Check if Chrome browser is available"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Try to initialize Chrome driver
        driver = webdriver.Chrome(
            service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        driver.quit()
        print("✓ Chrome browser and WebDriver are available")
        return True
    except Exception as e:
        print(f"✗ Chrome setup issue: {e}")
        print("Please ensure Chrome browser is installed")
        return False

def start_server():
    """Start the FastAPI server"""
    print("Starting FastAPI server...")
    
    # Change to the project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    try:
        # Start uvicorn server
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "backend.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ]
        
        process = subprocess.Popen(cmd)
        
        # Wait a moment for server to start
        print("Waiting for server to start...")
        time.sleep(3)
        
        # Open browser
        print("Opening web browser...")
        webbrowser.open("http://localhost:8000")
        
        print("\n" + "="*60)
        print("🚀 Google Maps Data Extractor is running!")
        print("📱 Web Interface: http://localhost:8000")
        print("📊 API Docs: http://localhost:8000/docs")
        print("⏹️  Press Ctrl+C to stop the server")
        print("="*60 + "\n")
        
        # Wait for the process
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
        process.terminate()
        process.wait()
        print("✓ Server stopped")
    except Exception as e:
        print(f"✗ Error starting server: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("🗺️  Google Maps Data Extractor")
    print("="*40)
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    # Check Chrome
    print("Checking Chrome browser...")
    if not check_chrome():
        print("Warning: Chrome check failed. The app may still work if Chrome is installed.")
    
    # Create necessary directories
    os.makedirs("temp", exist_ok=True)
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()

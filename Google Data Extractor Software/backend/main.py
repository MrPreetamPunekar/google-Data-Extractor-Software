from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import pandas as pd
from typing import Optional, Dict, List
import os
import sys
from datetime import datetime
import asyncio
import uuid
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from backend.scraper import GoogleMapsScraper
from backend.utils import create_csv_file

# Ensure temp directory exists
os.makedirs("temp", exist_ok=True)

app = FastAPI(title="Google Maps Data Extractor API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Store scraping results and progress in memory
scraping_sessions = {}

class ScrapeRequest(BaseModel):
    keywords: str
    location: str
    max_results: int

class ScrapeSession:
    def __init__(self, session_id: str, keywords: str, location: str, max_results: int):
        self.session_id = session_id
        self.keywords = keywords
        self.location = location
        self.max_results = max_results
        self.status = "idle"
        self.completed = 0
        self.total = max_results
        self.results = []
        self.error_message = None
        self.start_time = None
        self.end_time = None

async def run_scraping_task(session: ScrapeSession):
    """Background task to run the scraping process"""
    try:
        session.status = "running"
        session.start_time = datetime.now()
        
        scraper = GoogleMapsScraper()
        
        # Update progress callback
        def progress_callback(completed, total):
            session.completed = completed
            session.total = total
        
        # Run scraping in thread pool to avoid blocking
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                scraper.scrape_google_maps_sync,
                session.keywords,
                session.location,
                session.max_results,
                progress_callback
            )
            results = future.result()
        
        session.results = results
        session.status = "completed"
        session.end_time = datetime.now()
        
    except Exception as e:
        session.status = "error"
        session.error_message = str(e)
        session.end_time = datetime.now()
        print(f"Scraping error: {e}")

@app.get("/")
async def read_root():
    """Serve the main page"""
    return FileResponse("frontend/index.html")

@app.post("/start_scraping")
async def start_scraping(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """Start a new scraping session"""
    try:
        # Validate input
        if not request.keywords or not request.location:
            raise HTTPException(status_code=400, detail="Keywords and location are required")
        
        if request.max_results <= 0 or request.max_results > 500:
            raise HTTPException(status_code=400, detail="Max results must be between 1 and 500")
        
        # Create new session
        session_id = str(uuid.uuid4())
        session = ScrapeSession(session_id, request.keywords, request.location, request.max_results)
        scraping_sessions[session_id] = session
        
        # Start background task
        background_tasks.add_task(run_scraping_task, session)
        
        return {"session_id": session_id, "status": "started"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/progress/{session_id}")
async def get_progress(session_id: str):
    """Get progress of a scraping session"""
    if session_id not in scraping_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = scraping_sessions[session_id]
    
    return {
        "session_id": session_id,
        "status": session.status,
        "completed": session.completed,
        "total": session.total,
        "progress_percentage": (session.completed / session.total * 100) if session.total > 0 else 0,
        "error_message": session.error_message,
        "start_time": session.start_time.isoformat() if session.start_time else None,
        "end_time": session.end_time.isoformat() if session.end_time else None
    }

@app.get("/results/{session_id}")
async def get_results(session_id: str):
    """Get results of a scraping session"""
    if session_id not in scraping_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = scraping_sessions[session_id]
    
    if session.status != "completed":
        raise HTTPException(status_code=400, detail="Scraping not completed yet")
    
    return {
        "session_id": session_id,
        "keywords": session.keywords,
        "location": session.location,
        "total_results": len(session.results),
        "results": session.results
    }

@app.get("/download_csv/{session_id}")
async def download_csv(session_id: str):
    """Download results as CSV file"""
    if session_id not in scraping_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = scraping_sessions[session_id]
    
    if session.status != "completed":
        raise HTTPException(status_code=400, detail="Scraping not completed yet")
    
    if not session.results:
        raise HTTPException(status_code=400, detail="No results to download")
    
    # Create CSV file
    csv_filename = create_csv_file(session.results, session.keywords, session.location)
    
    return FileResponse(
        path=csv_filename,
        filename=f"google_maps_data_{session.keywords}_{session.location}.csv",
        media_type="text/csv"
    )

@app.get("/download_json/{session_id}")
async def download_json(session_id: str):
    """Download results as JSON file"""
    if session_id not in scraping_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = scraping_sessions[session_id]
    
    if session.status != "completed":
        raise HTTPException(status_code=400, detail="Scraping not completed yet")
    
    if not session.results:
        raise HTTPException(status_code=400, detail="No results to download")
    
    # Create JSON file
    json_data = {
        "metadata": {
            "keywords": session.keywords,
            "location": session.location,
            "total_results": len(session.results),
            "scraped_at": session.end_time.isoformat() if session.end_time else None
        },
        "results": session.results
    }
    
    json_filename = f"temp/google_maps_data_{session_id}.json"
    os.makedirs("temp", exist_ok=True)
    
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    return FileResponse(
        path=json_filename,
        filename=f"google_maps_data_{session.keywords}_{session.location}.json",
        media_type="application/json"
    )

@app.get("/sessions")
async def list_sessions():
    """List all scraping sessions"""
    sessions_info = []
    for session_id, session in scraping_sessions.items():
        sessions_info.append({
            "session_id": session_id,
            "keywords": session.keywords,
            "location": session.location,
            "status": session.status,
            "completed": session.completed,
            "total": session.total,
            "start_time": session.start_time.isoformat() if session.start_time else None
        })
    
    return {"sessions": sessions_info}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

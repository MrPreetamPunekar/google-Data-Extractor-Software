# Google Maps Data Extractor Web App

A full-stack web application that extracts business data from Google Maps search results using Selenium automation.

## Features

- **Web Interface**: Simple HTML/CSS/JavaScript frontend for easy interaction
- **Real-time Progress**: Live progress tracking during scraping operations
- **Data Export**: Download results in CSV or JSON format
- **Comprehensive Data**: Extracts business name, address, phone, website, rating, reviews, categories, hours, and coordinates
- **Error Handling**: Robust error handling with retry mechanisms
- **Headless Scraping**: Uses headless Chrome for efficient data extraction

## Project Structure

```
google_maps_extractor/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── scraper.py           # Selenium scraping logic
│   ├── database.py          # SQLite database operations
│   └── utils.py             # Helper functions
├── frontend/
│   ├── index.html          # Main web interface
│   ├── styles.css          # Styling
│   └── script.js           # Frontend JavaScript
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Chrome browser (for Selenium WebDriver)
- pip (Python package manager)

### Setup Steps

1. **Clone or download the project files**

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Chrome WebDriver**
   The application uses `webdriver-manager` to automatically download and manage ChromeDriver, so no manual installation is required.

## Usage

### Starting the Application

1. **Start the backend server**
   ```bash
   python -m backend.main
   ```
   
   Or alternatively:
   ```bash
   cd backend
   python main.py
   ```

2. **Access the web interface**
   Open your browser and navigate to: `http://localhost:8000`

### Using the Web Interface

1. **Enter Search Parameters**
   - **Keywords**: What you're searching for (e.g., "restaurants", "hotels", "dentists")
   - **Location**: Where to search (e.g., "New York, NY", "Los Angeles, CA")
   - **Max Results**: Number of results to scrape (1-500)

2. **Start Scraping**
   - Click "Start Scraping" button
   - Monitor real-time progress
   - Wait for completion

3. **View and Download Results**
   - Review results in the data table
   - Download as CSV or JSON format
   - Results include all extracted business information

## API Endpoints

The backend provides the following REST API endpoints:

- `POST /start_scraping` - Start a new scraping session
- `GET /progress/{session_id}` - Get scraping progress
- `GET /results/{session_id}` - Get scraping results
- `GET /download_csv/{session_id}` - Download CSV file
- `GET /download_json/{session_id}` - Download JSON file
- `GET /sessions` - List all scraping sessions

## Data Fields Extracted

For each business, the scraper attempts to extract:

- **Name**: Business name
- **Address**: Full address
- **Phone**: Phone number
- **Website**: Website URL
- **Rating**: Star rating (1-5)
- **Reviews**: Number of reviews
- **Categories**: Business categories/types
- **Hours**: Operating hours
- **Coordinates**: Latitude and longitude

## Configuration

### Scraping Settings

The scraper includes several built-in features for reliable operation:

- **Random Delays**: Prevents detection by varying request timing
- **Headless Mode**: Runs Chrome in background for efficiency
- **Error Handling**: Graceful handling of missing elements
- **Progress Tracking**: Real-time updates on scraping progress

### Rate Limiting

The application includes random delays between requests to respect Google's servers and avoid being blocked. Typical delays range from 0.5 to 2 seconds between actions.

## Troubleshooting

### Common Issues

1. **Chrome Driver Issues**
   - The app automatically downloads ChromeDriver
   - Ensure Chrome browser is installed
   - Check internet connection for driver download

2. **Scraping Blocked**
   - Google may temporarily block requests
   - Try reducing the number of results
   - Wait before retrying
   - Consider using a VPN if consistently blocked

3. **Missing Data**
   - Some businesses may not have all information available
   - The scraper handles missing data gracefully
   - Check the error logs for specific issues

4. **Performance Issues**
   - Large result sets (200+) may take significant time
   - Consider breaking large requests into smaller batches
   - Monitor system resources during scraping

### Error Messages

- **"Failed to start scraping"**: Check input parameters and try again
- **"Session not found"**: The scraping session may have expired
- **"Scraping not completed yet"**: Wait for the process to finish
- **"No results to download"**: The scraping found no matching businesses

## Legal and Ethical Considerations

### Important Notes

- **Respect robots.txt**: Always check and respect website policies
- **Rate Limiting**: Don't overwhelm servers with too many requests
- **Data Usage**: Use scraped data responsibly and in compliance with terms of service
- **Commercial Use**: Be aware of legal implications for commercial data usage

### Best Practices

- Use reasonable delays between requests
- Don't scrape excessively large datasets
- Respect website terms of service
- Consider official APIs when available
- Use data for legitimate purposes only

## Development

### Running in Development Mode

For development, you can run the FastAPI server with auto-reload:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Database

The application uses SQLite for storing scraping sessions and results. The database file (`google_maps_data.db`) is created automatically in the project directory.

### Extending the Application

The modular structure makes it easy to extend:

- **Add new data fields**: Modify the scraper.py extraction methods
- **New export formats**: Add handlers in utils.py
- **Enhanced UI**: Modify frontend files
- **Additional APIs**: Extend main.py with new endpoints

## Dependencies

### Backend Dependencies

- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `selenium`: Web automation
- `pandas`: Data manipulation
- `webdriver-manager`: Chrome driver management
- `pydantic`: Data validation
- `aiofiles`: Async file operations

### Frontend Dependencies

- Vanilla JavaScript (no external dependencies)
- Font Awesome icons (CDN)
- Modern CSS with flexbox and grid

## Support

For issues, questions, or contributions:

1. Check the troubleshooting section
2. Review error logs in the console
3. Ensure all dependencies are properly installed
4. Verify Chrome browser is available

## License

This project is for educational and research purposes. Please ensure compliance with applicable laws and website terms of service when using this tool.

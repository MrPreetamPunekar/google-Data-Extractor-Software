import pandas as pd
import os
from typing import List, Dict
from datetime import datetime
import json

def create_csv_file(results: List[Dict], keywords: str, location: str) -> str:
    """
    Convert scraping results to CSV file
    
    Args:
        results: List of dictionaries containing business data
        keywords: Search keywords used
        location: Location searched
        
    Returns:
        str: Path to the created CSV file
    """
    try:
        # Create temp directory if it doesn't exist
        os.makedirs("temp", exist_ok=True)
        
        # Convert results to DataFrame
        df = pd.DataFrame(results)
        
        # Handle nested dictionaries (hours and coordinates)
        if 'hours' in df.columns:
            df['hours'] = df['hours'].apply(lambda x: json.dumps(x, ensure_ascii=False))
        if 'coordinates' in df.columns:
            df['latitude'] = df['coordinates'].apply(lambda x: x.get('latitude', ''))
            df['longitude'] = df['coordinates'].apply(lambda x: x.get('longitude', ''))
            df.drop('coordinates', axis=1, inplace=True)
            
        # Handle lists (categories)
        if 'categories' in df.columns:
            df['categories'] = df['categories'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
            
        # Clean up reviews count
        if 'reviews_count' in df.columns:
            df['reviews_count'] = df['reviews_count'].apply(
                lambda x: x.replace('reviews', '').replace('(', '').replace(')', '').strip() if isinstance(x, str) else x
            )
            
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"temp/google_maps_data_{keywords}_{location}_{timestamp}.csv"
        
        # Save to CSV
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        return filename
        
    except Exception as e:
        print(f"Error creating CSV file: {str(e)}")
        raise

def clean_filename(filename: str) -> str:
    """
    Clean filename by removing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        str: Cleaned filename
    """
    # Replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def format_business_hours(hours_dict: Dict) -> str:
    """
    Format business hours dictionary to string
    
    Args:
        hours_dict: Dictionary containing business hours
        
    Returns:
        str: Formatted business hours string
    """
    if not hours_dict:
        return ""
        
    formatted_hours = []
    for day, hours in hours_dict.items():
        formatted_hours.append(f"{day}: {hours}")
    return "\n".join(formatted_hours)

def parse_reviews_count(reviews_str: str) -> int:
    """
    Parse reviews count string to integer
    
    Args:
        reviews_str: String containing reviews count
        
    Returns:
        int: Number of reviews
    """
    try:
        # Remove non-numeric characters and convert to int
        reviews = ''.join(filter(str.isdigit, reviews_str))
        return int(reviews) if reviews else 0
    except:
        return 0

def parse_rating(rating_str: str) -> float:
    """
    Parse rating string to float
    
    Args:
        rating_str: String containing rating
        
    Returns:
        float: Rating value
    """
    try:
        return float(rating_str.split()[0])
    except:
        return 0.0

def create_error_response(error_message: str, status_code: int = 500) -> Dict:
    """
    Create standardized error response
    
    Args:
        error_message: Error message
        status_code: HTTP status code
        
    Returns:
        dict: Error response dictionary
    """
    return {
        "error": {
            "message": error_message,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat()
        }
    }

import sqlite3
import json
from typing import List, Dict, Optional
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, db_path: str = "google_maps_data.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize the database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create scraping sessions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS scraping_sessions (
                        id TEXT PRIMARY KEY,
                        keywords TEXT NOT NULL,
                        location TEXT NOT NULL,
                        max_results INTEGER NOT NULL,
                        status TEXT NOT NULL,
                        start_time TIMESTAMP,
                        end_time TIMESTAMP,
                        total_results INTEGER DEFAULT 0,
                        error_message TEXT
                    )
                ''')
                
                # Create businesses table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS businesses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        name TEXT,
                        address TEXT,
                        phone TEXT,
                        website TEXT,
                        rating REAL,
                        reviews_count INTEGER,
                        categories TEXT,
                        hours TEXT,
                        latitude REAL,
                        longitude REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES scraping_sessions (id)
                    )
                ''')
                
                conn.commit()
                print("Database initialized successfully")
                
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            raise

    def save_session(self, session_id: str, keywords: str, location: str, 
                    max_results: int, status: str = "started") -> bool:
        """Save a new scraping session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO scraping_sessions 
                    (id, keywords, location, max_results, status, start_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (session_id, keywords, location, max_results, status, datetime.now()))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving session: {str(e)}")
            return False

    def update_session_status(self, session_id: str, status: str, 
                            error_message: Optional[str] = None) -> bool:
        """Update session status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if status == "completed" or status == "error":
                    cursor.execute('''
                        UPDATE scraping_sessions 
                        SET status = ?, end_time = ?, error_message = ?
                        WHERE id = ?
                    ''', (status, datetime.now(), error_message, session_id))
                else:
                    cursor.execute('''
                        UPDATE scraping_sessions 
                        SET status = ?, error_message = ?
                        WHERE id = ?
                    ''', (status, error_message, session_id))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating session status: {str(e)}")
            return False

    def save_businesses(self, session_id: str, businesses: List[Dict]) -> bool:
        """Save business data to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for business in businesses:
                    # Extract coordinates
                    coords = business.get('coordinates', {})
                    latitude = coords.get('latitude') if coords else None
                    longitude = coords.get('longitude') if coords else None
                    
                    # Convert lists and dicts to JSON strings
                    categories = json.dumps(business.get('categories', []))
                    hours = json.dumps(business.get('hours', {}))
                    
                    # Parse reviews count
                    reviews_count = self._parse_reviews_count(business.get('reviews_count', ''))
                    
                    # Parse rating
                    rating = self._parse_rating(business.get('rating', ''))
                    
                    cursor.execute('''
                        INSERT INTO businesses 
                        (session_id, name, address, phone, website, rating, 
                         reviews_count, categories, hours, latitude, longitude)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        session_id,
                        business.get('name', ''),
                        business.get('address', ''),
                        business.get('phone', ''),
                        business.get('website', ''),
                        rating,
                        reviews_count,
                        categories,
                        hours,
                        latitude,
                        longitude
                    ))
                
                # Update total results count in session
                cursor.execute('''
                    UPDATE scraping_sessions 
                    SET total_results = ?
                    WHERE id = ?
                ''', (len(businesses), session_id))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error saving businesses: {str(e)}")
            return False

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session information"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM scraping_sessions WHERE id = ?
                ''', (session_id,))
                
                row = cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                return None
                
        except Exception as e:
            print(f"Error getting session: {str(e)}")
            return None

    def get_businesses(self, session_id: str) -> List[Dict]:
        """Get businesses for a session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM businesses WHERE session_id = ?
                    ORDER BY id
                ''', (session_id,))
                
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                businesses = []
                for row in rows:
                    business = dict(zip(columns, row))
                    
                    # Parse JSON fields back to objects
                    try:
                        business['categories'] = json.loads(business['categories'])
                    except:
                        business['categories'] = []
                    
                    try:
                        business['hours'] = json.loads(business['hours'])
                    except:
                        business['hours'] = {}
                    
                    # Add coordinates as nested dict
                    if business['latitude'] and business['longitude']:
                        business['coordinates'] = {
                            'latitude': business['latitude'],
                            'longitude': business['longitude']
                        }
                    else:
                        business['coordinates'] = {}
                    
                    businesses.append(business)
                
                return businesses
                
        except Exception as e:
            print(f"Error getting businesses: {str(e)}")
            return []

    def get_all_sessions(self) -> List[Dict]:
        """Get all scraping sessions"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM scraping_sessions 
                    ORDER BY start_time DESC
                ''')
                
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            print(f"Error getting all sessions: {str(e)}")
            return []

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its businesses"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete businesses first (foreign key constraint)
                cursor.execute('DELETE FROM businesses WHERE session_id = ?', (session_id,))
                
                # Delete session
                cursor.execute('DELETE FROM scraping_sessions WHERE id = ?', (session_id,))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error deleting session: {str(e)}")
            return False

    def _parse_reviews_count(self, reviews_str: str) -> int:
        """Parse reviews count string to integer"""
        try:
            reviews = ''.join(filter(str.isdigit, str(reviews_str)))
            return int(reviews) if reviews else 0
        except:
            return 0

    def _parse_rating(self, rating_str: str) -> float:
        """Parse rating string to float"""
        try:
            return float(str(rating_str).split()[0])
        except:
            return 0.0

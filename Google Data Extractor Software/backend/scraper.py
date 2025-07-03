from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import random
import asyncio
from typing import List, Dict, Callable
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleMapsScraper:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.setup_driver()

    def setup_driver(self):
        """Initialize Chrome driver with appropriate options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            logger.info("Chrome driver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {str(e)}")
            raise

    def scrape_google_maps_sync(self, keywords: str, location: str, max_results: int, 
                               progress_callback: Callable[[int, int], None]) -> List[Dict]:
        """Main scraping function (synchronous)"""
        try:
            results = []
            search_query = f"{keywords} in {location}"
            
            # Navigate to Google Maps
            self.driver.get("https://www.google.com/maps")
            time.sleep(random.uniform(2, 4))
            
            # Find and fill the search box
            search_box = self.wait.until(
                EC.presence_of_element_located((By.ID, "searchboxinput"))
            )
            search_box.clear()
            search_box.send_keys(search_query)
            search_box.send_keys(Keys.ENTER)
            
            # Wait for results to load
            time.sleep(random.uniform(3, 5))
            
            # Scroll through results
            scrolls_needed = max_results // 20  # Approximate number of results per scroll
            results_found = 0
            
            for scroll in range(scrolls_needed):
                try:
                    # Find the results container
                    results_panel = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
                    )
                    
                    # Scroll to load more results
                    self.driver.execute_script(
                        "arguments[0].scrollTop = arguments[0].scrollHeight", 
                        results_panel
                    )
                    
                    # Random delay between scrolls
                    time.sleep(random.uniform(1, 2))
                    
                    # Update progress
                    results_found = len(results)
                    progress_callback(results_found, max_results)
                    
                    if results_found >= max_results:
                        break
                        
                except Exception as e:
                    logger.warning(f"Error during scrolling: {str(e)}")
                    continue
            
            # Extract business listings
            listings = self.driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
            
            for idx, listing in enumerate(listings[:max_results]):
                try:
                    # Click on listing to view details
                    listing.click()
                    time.sleep(random.uniform(1, 2))
                    
                    # Extract business details
                    business_data = self._extract_business_details()
                    results.append(business_data)
                    
                    # Update progress
                    progress_callback(len(results), max_results)
                    
                    # Random delay between extractions
                    time.sleep(random.uniform(0.5, 1.5))
                    
                except Exception as e:
                    logger.warning(f"Error extracting business details: {str(e)}")
                    continue
            
            logger.info(f"Scraping completed. Found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Scraping failed: {str(e)}")
            raise
        
        finally:
            if self.driver:
                self.driver.quit()

    def _extract_business_details(self) -> Dict:
        """Extract details from the business panel"""
        try:
            # Wait for business panel to load
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.fontHeadlineSmall"))
            )
            
            # Extract business information
            business_info = {
                "name": self._safe_extract_text("div.fontHeadlineSmall"),
                "address": self._safe_extract_text("button[data-item-id='address']"),
                "phone": self._safe_extract_text("button[data-item-id='phone:tel']"),
                "website": self._safe_extract_attribute("a[data-item-id='authority']", "href"),
                "rating": self._safe_extract_text("span.fontDisplayLarge"),
                "reviews_count": self._safe_extract_text("button[jsaction='pane.rating.moreReviews']"),
                "categories": self._extract_categories(),
                "hours": self._extract_hours(),
                "coordinates": self._extract_coordinates()
            }
            
            return business_info
            
        except Exception as e:
            logger.warning(f"Error in business details extraction: {str(e)}")
            return {}

    def _safe_extract_text(self, selector: str) -> str:
        """Safely extract text from an element"""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            return element.text.strip()
        except:
            return ""

    def _safe_extract_attribute(self, selector: str, attribute: str) -> str:
        """Safely extract attribute from an element"""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            return element.get_attribute(attribute)
        except:
            return ""

    def _extract_categories(self) -> List[str]:
        """Extract business categories"""
        try:
            categories_element = self.driver.find_element(
                By.CSS_SELECTOR, 
                "button[jsaction='pane.rating.category']"
            )
            return [cat.strip() for cat in categories_element.text.split('·')]
        except:
            return []

    def _extract_hours(self) -> Dict[str, str]:
        """Extract business hours"""
        hours = {}
        try:
            # Click to expand hours
            hours_button = self.driver.find_element(
                By.CSS_SELECTOR,
                "button[data-item-id='oh']"
            )
            hours_button.click()
            time.sleep(0.5)
            
            # Extract hours for each day
            hours_elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                "table tr"
            )
            
            for element in hours_elements:
                try:
                    day = element.find_element(By.CSS_SELECTOR, "th").text.strip()
                    time_range = element.find_element(By.CSS_SELECTOR, "td").text.strip()
                    hours[day] = time_range
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"Error extracting hours: {str(e)}")
            
        return hours

    def _extract_coordinates(self) -> Dict[str, float]:
        """Extract latitude and longitude"""
        try:
            url = self.driver.current_url
            coords = {}
            
            # Extract coordinates from URL
            if "@" in url:
                lat_lng = url.split("@")[1].split(",")[:2]
                coords["latitude"] = float(lat_lng[0])
                coords["longitude"] = float(lat_lng[1])
            
            return coords
            
        except Exception as e:
            logger.warning(f"Error extracting coordinates: {str(e)}")
            return {}

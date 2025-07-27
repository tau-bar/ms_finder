import os
from typing import List, Dict, Any
from sheets_service import fetch_locations as fetch_sheets_locations
from api_service import fetch_api_locations
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fetch_all_locations() -> List[Dict[str, Any]]:
    """Fetch musollah locations based on the configured scope.
    
    This function fetches data from Google Sheets and optionally from the musollah.com API
    based on the SCOPE environment variable:
    - If SCOPE is 'sg', data is fetched from both Google Sheets and the API
    - If SCOPE is 'nus' or undefined, data is fetched only from Google Sheets
    
    Returns:
        List of dictionaries containing musollah location data with keys:
        - name: Name of the musollah
        - lat: Latitude (float)
        - lon: Longitude (float)
        - directions: Directions to the musollah
        - details: Additional details about the musollah
        - google_maps: Google Maps link to the location
    """
    # Get the scope from environment variables
    scope = os.getenv("SCOPE", "nus").lower()

    data_fetchers = {
        "nus": [fetch_sheets_locations],
        "sg": [fetch_sheets_locations, fetch_api_locations]
    }
    
    all_locations = []
    for fetcher in data_fetchers[scope]:
        all_locations.extend(fetcher())
    print(f"Fetched {len(all_locations)} locations for {scope}")
    
    return all_locations
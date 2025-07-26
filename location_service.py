from typing import List, Dict, Any
from sheets_service import fetch_locations as fetch_sheets_locations
from api_service import fetch_api_locations

def fetch_all_locations() -> List[Dict[str, Any]]:
    """Fetch musollah locations from all available sources.
    
    This function combines data from both Google Sheets and the musollah.com API.
    
    Returns:
        List of dictionaries containing musollah location data with keys:
        - name: Name of the musollah
        - lat: Latitude (float)
        - lon: Longitude (float)
        - directions: Directions to the musollah
        - details: Additional details about the musollah
        - google_maps: Google Maps link to the location
    """
    # Fetch locations from Google Sheets
    sheets_locations = fetch_sheets_locations()
    
    # Fetch locations from API
    api_locations = fetch_api_locations()
    
    # Combine both sources
    all_locations = sheets_locations + api_locations
    
    # Log the number of locations from each source
    print(f"Fetched {len(sheets_locations)} locations from Google Sheets")
    print(f"Fetched {len(api_locations)} locations from API")
    print(f"Total: {len(all_locations)} locations")
    
    return all_locations
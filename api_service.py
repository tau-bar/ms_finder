import os
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Environment variables
API_KEY = os.getenv('MUSOLLAH_API_KEY')
API_URL = "https://api.musollah.com/info/musollah/list/sg"

def fetch_api_locations() -> List[Dict[str, Any]]:
    """Fetch musollah locations from the musollah.com API.
    
    Returns:
        List of dictionaries containing musollah location data with keys:
        - name: Name of the musollah
        - lat: Latitude (float)
        - lon: Longitude (float)
        - directions: Directions to the musollah
        - details: Additional details about the musollah
        - google_maps: Google Maps link to the location (constructed)
    """
    try:
        # Set up the API request with the API key
        headers = {"X-API-KEY": API_KEY}
        
        # Make the API request
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the JSON response
        data = response.json()
        
        if not data:
            print('No data found from the API.')
            return []
        
        # Convert API data to location dictionaries in the same format as sheets_service
        locations = []
        
        for item in data:
            try:
                # Extract and convert latitude and longitude to float
                lat = float(item.get('Latitude', 0))
                lon = float(item.get('Longitude', 0))
                
                # Create location dictionary with the same structure as sheets_service
                name = f"{item.get('Place', 'Unknown')}"
                location = {
                    "name": name,
                    "lat": lat,
                    "lon": lon,
                    "address": item.get('Address', ''),
                    "details": item.get('Details', ''),
                    "type": item.get('Type', 'Musollah'),
                    "directions": item.get('LocationIn', ''),
                    # Construct Google Maps link
                    # "google_maps": f"https://www.google.com/maps/search/?api=1&query={name.replace(" ", "+")},{lat},{lon}",
                }
                
                locations.append(location)
            except (ValueError, TypeError) as e:
                print(f"Error processing item {item.get('ID', 'unknown')}: {e}")
                continue
        
        return locations
    except Exception as e:
        print(f"Error fetching data from API: {e}")
        return []

# For testing purposes
if __name__ == "__main__":
    locations = fetch_api_locations()
    print(f"Fetched {len(locations)} locations from API")
    for loc in locations[:2]:  # Print first two locations as a sample
        print(f"Name: {loc['name']}")
        print(f"Coordinates: {loc['lat']}, {loc['lon']}")
        print(f"Directions: {loc['directions'][:50]}...")
        print(f"Details: {loc['details'][:50]}...")
        print(f"Google Maps: {loc['google_maps']}")
        print("---")
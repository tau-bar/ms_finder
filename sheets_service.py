import os
from typing import List, Dict, Any
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Environment variables
SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
API_KEY = os.getenv('GOOGLE_SHEETS_API_KEY')
RANGE_NAME = os.getenv('GOOGLE_SHEETS_RANGE', 'Sheet1')

def fetch_locations() -> List[Dict[str, Any]]:
    """Fetch musollah locations from Google Sheets using API key.
    
    Returns:
        List of dictionaries containing musollah location data with keys:
        - name: Name of the musollah
        - lat: Latitude (float)
        - lon: Longitude (float)
        - directions: Directions to the musollah
        - details: Additional details about the musollah
        - google_maps: Google Maps link to the location
    """
    try:
        # Build the service with API key instead of OAuth credentials
        service = build('sheets', 'v4', developerKey=API_KEY)
        
        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                   range=RANGE_NAME).execute()
        values = result.get('values', [])
        
        if not values:
            print('No data found in the Google Sheet.')
            return []
        
        # Convert sheet data to location dictionaries
        locations = []
        
        # Skip the header row (first row)
        if values and len(values) > 0:
            data_rows = values[1:]
            
            for row in data_rows:
                # Ensure the row has the minimum required fields
                if len(row) >= 5:  # At minimum, we need the first 5 columns
                    try:
                        location = {
                            "name": row[0],
                            "lat": float(row[1]),
                            "lon": float(row[2]),
                            "directions": row[3],
                            "details": row[4],
                        }
                        
                        # Add Google Maps link if available
                        if len(row) >= 6:
                            location["google_maps"] = row[5]
                            
                        locations.append(location)
                    except (ValueError, TypeError) as e:
                        print(f"Error processing row {row}: {e}")
                        continue
        
        return locations
    except Exception as e:
        print(f"Error fetching data from Google Sheets: {e}")
        return []

# For testing purposes
if __name__ == "__main__":
    locations = fetch_locations()
    print(f"Fetched {len(locations)} locations from Google Sheets")
    for loc in locations[:2]:  # Print first two locations as a sample
        print(f"Name: {loc['name']}")
        print(f"Coordinates: {loc['lat']}, {loc['lon']}")
        print(f"Directions: {loc['directions'][:50]}...")
        print(f"Google Maps: {loc['google_maps']}")
        print("---")
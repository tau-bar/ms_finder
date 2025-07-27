import os
from typing import List, Dict, Any, TypeVar
from googleapiclient.discovery import build
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Environment variables
SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
API_KEY = os.getenv('GOOGLE_SHEETS_API_KEY')
LOCATIONS_RANGE_NAME = os.getenv('GOOGLE_SHEETS_RANGE', 'locations')

# Define a schema for the columns
# Each entry defines: 
# - key: the dictionary key to use in the result
# - required: whether this field is required
# - transform: optional function to transform the value (e.g., convert to float)
# - default: default value if the column is missing or empty
COLUMN_SCHEMA = [
    {
        "index": 0,
        "key": "name",
        "required": True,
        "transform": None,
        "default": None
    },
    {
        "index": 1,
        "key": "lat",
        "required": True,
        "transform": float,
        "default": None
    },
    {
        "index": 2,
        "key": "lon",
        "required": True,
        "transform": float,
        "default": None
    },
        {
        "index": 3,
        "key": "address",
        "required": False,
        "transform": None,
        "default": None
    },
    {
        "index": 4,
        "key": "directions",
        "required": False,
        "transform": None,
        "default": None
    },
    {
        "index": 5,
        "key": "details",
        "required": True,
        "transform": None,
        "default": "No additional details available"
    },
    {
        "index": 6,
        "key": "google_maps",
        "required": False,
        "transform": None,
        "default": None
    },
    {
        "index": 7,
        "key": "type",
        "required": False,
        "transform": None,
        "default": "Musollah"
    },
    {
        "index": 8,
        "key": "guide",
        "required": False,
        "transform": None,
        "default": None
    }
    # Add new columns here following the same pattern
    # {
    #     "index": 7,
    #     "key": "new_column_name",
    #     "required": False,
    #     "transform": None,
    #     "default": "Default value"
    # },
]

def get_column_value(row: List[str], column_def: Dict[str, Any]) -> Any:
    """Extract a column value from a row based on the column definition."""
    index = column_def["index"]
    transform = column_def["transform"]
    default = column_def["default"]
    
    # Check if the column exists in the row
    if len(row) > index and row[index]:
        value = row[index]
        # Apply transformation if provided
        if transform is not None:
            try:
                return transform(value)
            except (ValueError, TypeError):
                return default
        return value
    return default

def fetch_locations() -> List[Dict[str, Any]]:
    """Fetch musollah locations from Google Sheets using API key.
    
    Returns:
        List of dictionaries containing musollah location data with keys defined in COLUMN_SCHEMA.
    """
    try:
        # Build the service with API key instead of OAuth credentials
        service = build('sheets', 'v4', developerKey=API_KEY)
        
        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                   range=LOCATIONS_RANGE_NAME).execute()
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
                try:
                    # Check if row has minimum required fields
                    required_columns = [col for col in COLUMN_SCHEMA if col["required"]]
                    if len(row) < max(col["index"] for col in required_columns) + 1:
                        print(f"Skipping row {row}: missing required columns")
                        continue
                    
                    # Build location dictionary using schema
                    location = {}
                    for column_def in COLUMN_SCHEMA:
                        location[column_def["key"]] = get_column_value(row, column_def)
                    
                    locations.append(location)
                except Exception as e:
                    print(f"Error processing row {row}: {e}")
                    continue
        
        return locations
    except Exception as e:
        print(f"Error fetching data from Google Sheets: {e}")
        return []

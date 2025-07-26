# Google Sheets Integration Setup Guide

This guide will help you set up the Google Sheets API integration for the Musollah Finder Telegram Bot using an API key for public sheets.

## 1. Create a Google Sheets Spreadsheet

1. Go to [Google Sheets](https://sheets.google.com) and create a new spreadsheet.
2. Set up the following columns in the first row:
   - A1: Name
   - B1: Latitude
   - C1: Longitude
   - D1: Directions
   - E1: Details
   - F1: Google Maps (link to the location on Google Maps)
3. Starting from row 2, add your musollah locations data.
4. Make note of the Spreadsheet ID in the URL: `https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit`
5. **Important**: Make sure your spreadsheet is public or shared with anyone with the link (read-only access is sufficient).
   - Click the "Share" button in the top right
   - Change access to "Anyone with the link" and set permission to "Viewer"

## 2. Set Up Google Cloud Project and Enable API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. In the sidebar, navigate to "APIs & Services" > "Library".
4. Search for "Google Sheets API" and enable it for your project.

## 3. Create API Key

1. In the Google Cloud Console, go to "APIs & Services" > "Credentials".
2. Click "Create Credentials" and select "API key".
3. Your API key will be created and displayed. Copy this key.
4. (Optional but recommended) Restrict the API key:
   - Click "Restrict Key"
   - Under "API restrictions", select "Restrict key"
   - Select "Google Sheets API" from the dropdown
   - Click "Save"

## 4. Update Environment Variables

1. Open your `.env` file.
2. Add the following variables:
   ```
   GOOGLE_SHEETS_API_KEY=your_api_key_here
   GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id_here
   GOOGLE_SHEETS_RANGE=Sheet1
   ```
3. Replace `your_api_key_here` with the API key you created in step 3.
4. Replace `your_spreadsheet_id_here` with your actual spreadsheet ID from step 1.
5. If your sheet name is different from "Sheet1", update the range accordingly.

## Spreadsheet Format

Ensure your Google Sheets data follows this format:

| Name | Latitude | Longitude | Directions | Details | Google Maps |
|------|----------|-----------|------------|--------|-------------|
| AS3 Musollah | 1.2946 | 103.7710 | Located at Level 6... | For safety and... | https://maps.google.com/?q=1.2946,103.7710 |
| AS4 Musollah | 1.2947 | 103.7719 | Located at Level 7... | For safety and... | https://maps.google.com/?q=1.2947,103.7719 |

## Troubleshooting

- If you encounter API errors, verify that your API key is correct and has not expired.
- Ensure the spreadsheet is set to public or "Anyone with the link" can view it.
- Check that the latitude and longitude values are properly formatted as numbers in Google Sheets.
- If you update the spreadsheet structure, you may need to update the `GOOGLE_SHEETS_RANGE` environment variable.
- If you see a "Quota exceeded" error, you may need to set up billing for your Google Cloud project or wait until the quota resets.
- Verify that the Google Sheets API is enabled in your Google Cloud project.
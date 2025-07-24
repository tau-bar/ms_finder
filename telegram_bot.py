import os
import logging
from dotenv import load_dotenv
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from geopy.distance import geodesic
from health_server import start_health_server

# Load environment variables from .env file
load_dotenv()

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f'To find the nearest musollah:\n\n'
        f'Tap the attachment icon (paperclip), select "Location", and send your current location.'
        )

async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_location = update.message.location
    latitude = user_location.latitude
    longitude = user_location.longitude
    
    # List of predefined locations (Musollah locations from NUSMS)
    locations = [
        # Faculty of Arts and Social Sciences
        {
            "name": "AS3 Musollah", 
            "lat": 1.2946, 
            "lon": 103.7710,
            "directions": "Located at Level 6 of Staircase 3 of AS3, beside the main lift (AS3-1). From AS2, head downstairs to the main garden with outdoor tables & chairs. Walk past that area until you reach the toilets. Take the lift opposite the toilets to Level 6. The musollah is at the staircase on the immediate right after exiting the lift.",
            "details": "For safety and hygiene purposes, please bring your own prayer paraphernalia & use the prayer spaces responsibly."
        },
        {
            "name": "AS4 Musollah", 
            "lat": 1.2947, 
            "lon": 103.7719,
            "directions": "Located at Level 7 staircase landing. Take Lift AS4-P1 up to Level 6. Exit lift, turn right and go up Staircase 2 by one level.",
            "details": "For safety and hygiene purposes, please bring your own prayer paraphernalia & use the prayer spaces responsibly."
        },
        {
            "name": "AS6 Musollah", 
            "lat": 1.2955, 
            "lon": 103.7723,
            "directions": "Located at Level 5 staircase landing, near the lift. Head to Level 2 of AS6. Enter through the glass door. Take the lift, AS6-1, to Level 5 and head to Staircase 1.",
            "details": "For safety and hygiene purposes, please bring your own prayer paraphernalia & use the prayer spaces responsibly."
        },
        {
            "name": "Central Library (CLB) Musollah", 
            "lat": 1.2966, 
            "lon": 103.7732,
            "directions": "From CLB bus stop, walk towards Central Library. Go up the big flight of stairs to Central Forum (area with circle tables). Continue straight until you reach the brick stairs (near the lift) and go up the stairs. Turn right into the narrow flight of stairs and go up.",
            "details": "For safety and hygiene purposes, please bring your own prayer paraphernalia & use the prayer spaces responsibly."
        },
        
        # College of Design & Engineering
        {
            "name": "EA Musollah", 
            "lat": 1.3000, 
            "lon": 103.7707,
            "directions": "Located at Level 7 Staircase landing, near the lifts. Take lift up to Level 7 from Lift Lobby 2 of EA building. Turn right upon exiting the lift and enter Staircase 1. Go one floor up.",
            "details": "For safety and hygiene purposes, please bring your own prayer paraphernalia & use the prayer spaces responsibly."
        },
        {
            "name": "E3 Musollah", 
            "lat": 1.3004, 
            "lon": 103.7702,
            "directions": "Located near male toilet of Level 6 staircase landing. Walk past Cheers and along the corridor of classrooms. Find Staircase 1 which is the first staircase to the left. Go to Level 6.",
            "details": "For safety and hygiene purposes, please bring your own prayer paraphernalia & use the prayer spaces responsibly."
        },
        {
            "name": "E5 Musollah", 
            "lat": 1.2998, 
            "lon": 103.7714,
            "directions": "Located at E5 Level 4 Staircase 1 landing. Take the lift near the seats with portable, up to the fourth floor.",
            "details": "For safety and hygiene purposes, please bring your own prayer paraphernalia & use the prayer spaces responsibly."
        },
        {
            "name": "SDE3 Musollah", 
            "lat": 1.2973, 
            "lon": 103.7704,
            "directions": "Head to SDE3 and take the lift to Level 4. After exiting the lift, walk straight and turn right. Keep walking till LT423. Turn right into the corridor between LT423 & LT424. At the end of the corridor turn right onto a corridor. At the end of the corridor, Staircase 4 is on the left. Take the stairs one floor up.",
            "details": "For safety and hygiene purposes, please bring your own prayer paraphernalia & use the prayer spaces responsibly."
        },
        
        # Faculty of Science & School of Medicine
        {
            "name": "S5 Musollah", 
            "lat": 1.2950, 
            "lon": 103.7781,
            "directions": "Located at the staircase landing near Science Library. At S5, take the lift up to Level 6. Turn left and enter the door to go up the staircase to reach the musollah.",
            "details": "For safety and hygiene purposes, please bring your own prayer paraphernalia & use the prayer spaces responsibly."
        },
        {
            "name": "MD6 Musollah", 
            "lat": 1.2956, 
            "lon": 103.7818,
            "directions": "Located below the stairs on the first level. Head to LT35 on the first floor. Enter Staircase 4 which is beside LT35.",
            "details": "For safety and hygiene purposes, please bring your own prayer paraphernalia & use the prayer spaces responsibly."
        },
        {
            "name": "MD3 Musollah", 
            "lat": 1.2947, 
            "lon": 103.7807,
            "directions": "Located at MD3 Level 1 staircase landing. Entrance through Stair 1.",
            "details": "For safety and hygiene purposes, please bring your own prayer paraphernalia & use the prayer spaces responsibly."
        },
        {
            "name": "Medicine-Science Library Musollah", 
            "lat": 1.2953, 
            "lon": 103.7801,
            "directions": "Located at Med Sci Library Level 4 staircase landing. Take Lift 1 up to level 3 and head up to Level 4 via Stair 2.",
            "details": "For safety and hygiene purposes, please bring your own prayer paraphernalia & use the prayer spaces responsibly."
        },
        {
            "name": "S1A Musollah", 
            "lat": 1.2929, 
            "lon": 103.7801,
            "directions": "Start from UHALL bus stop. Walk towards Medicine/School of Public Health (Science Drive 4). Cross the road safely to the other side, follow the pavement, and walk straight ahead until you reach the end. Walk up the stairs, turn left, and walk straight ahead. When you see blind corner mirror, turn right and right again. Enter the 'Stair 3' door. S1A musollah is located at the ground floor.",
            "details": "For safety and hygiene purposes, please bring your own prayer paraphernalia & use the prayer spaces responsibly."
        },
        
        # School of Computing
        {
            "name": "COM1 Main Foyer Musollah", 
            "lat": 1.2949, 
            "lon": 103.7737,
            "directions": "Find a staircase landing on the right side of COM1, facing COM2, near the Security Post, and open the door. Located at the Top of the staircase (Level 4).",
            "details": "For safety and hygiene purposes, please bring your own prayer paraphernalia & use the prayer spaces responsibly."
        },
        {
            "name": "COM1 Behind Dean's Office Musollah", 
            "lat": 1.2952, 
            "lon": 103.7740,
            "directions": "Staircase outside of Seminar Room 1 (SR 1), between Makerspace and the toilet. Located at the Highest floor (Level 3.5), right before the rooftop entrance. The backdoor of the Dean's Office can be seen on the way up.",
            "details": "For safety and hygiene purposes, please bring your own prayer paraphernalia & use the prayer spaces responsibly."
        },
        {
            "name": "COM3 Quiet Room", 
            "lat": 1.2941, 
            "lon": 103.7739,
            "directions": "Located in COM3-02-68.",
            "details": "This room can only be accessed by Computing PHD students & staff. For safety and hygiene purposes, please bring your own prayer paraphernalia & use the prayer spaces responsibly."
        },
        
        # NUS Business School
        {
            "name": "BIZ2 Musollah", 
            "lat": 1.2934, 
            "lon": 103.7744,
            "directions": "Start at COM2 bus stop. Walk through the canteen towards BIZ2 building. Upon reaching the BizAd society room, turn right. Continue walking towards the BIZ2 building. Before entering, take a right turn and locate Stair 1, opposite a toilet. Climb Stair 1 to level 6 staircase landing. End at level 6 staircase landing before roof access.",
            "details": "For safety and hygiene purposes, please bring your own prayer paraphernalia & use the prayer spaces responsibly."
        },
        {
            "name": "Hon Sui Sen Memorial Library Musollah", 
            "lat": 1.2925, 
            "lon": 103.7742,
            "directions": "Alight at bus stop \"OPP HSSML\". Cross the road and enter HSSML building from the nearside entrance. Take the stairs and turn right to reach the lift (HSS - P2). Take the lift to level 4. Exit the lift, turn right, and walk to Stair 1. Climb the flight of stairs to the roof access level. The musollah is located on the staircase landing.",
            "details": "For safety and hygiene purposes, please bring your own prayer paraphernalia & use the prayer spaces responsibly."
        },
        
        # University Town
        {
            "name": "Stephen Riady Centre Musollah", 
            "lat": 1.3046, 
            "lon": 103.7720,
            "directions": "Located on Level 2 at Staircase 5 landing, beside Flavours@UTown. Enter the stairwell near the lifts which are opposite the toilets.",
            "details": "For safety and hygiene purposes, please bring your own prayer paraphernalia & use the prayer spaces responsibly."
        },
        {
            "name": "Education Resource Centre Musollah", 
            "lat": 1.3059, 
            "lon": 103.7727,
            "directions": "Start from UTOWN bus stop. Walk towards Education Resource Centre (ERC). Follow the sheltered walkway throughout on the right side of the open field, straight ahead. Walk up the stairs. Walk slightly to your right, and then straight ahead. Once you see the top hanging sign, turn right and then turn left, enter the 'Starcase 3' door. You will reach the musollah by walking up the stairs.",
            "details": "For safety and hygiene purposes, please bring your own prayer paraphernalia & use the prayer spaces responsibly."
        },
        
        # Others
        {
            "name": "MPSH1 Musollah", 
            "lat": 1.3003, 
            "lon": 103.7747,
            "directions": "Located past the toilets. After you have passed the toilets, continue walking down the corridor until you reach the staircase landing near the lockers.",
            "details": "For safety and hygiene purposes, please bring your own prayer paraphernalia & use the prayer spaces responsibly."
        },
        {
            "name": "University Hall Musollah", 
            "lat": 1.2977, 
            "lon": 103.7784,
            "directions": "Located beside the security office at the University Hall, Lee Kong Chian Wing (LKCW), Level 1. Enter the building and follow the sign leading towards the security office and the toilets.",
            "details": "For safety and hygiene purposes, please bring your own prayer paraphernalia & use the prayer spaces responsibly."
        },
        
        # Nearby Mosques
        {
            "name": "Ahmad Mosque", 
            "lat": 1.3075, 
            "lon": 103.7694,
            "directions": "2 Lor Sarhad, Singapore 119173.",
            "details": "Public mosque near NUS."
        },
        {
            "name": "Tentera Di Raja Mosque", 
            "lat": 1.3294, 
            "lon": 103.7673,
            "directions": "81 Clementi Road, Singapore 129797.",
            "details": "Public mosque near NUS."
        },
        {
            "name": "Darussalam Mosque", 
            "lat": 1.3083, 
            "lon": 103.7646,
            "directions": "3002 Commonwealth Ave W, Singapore 129579.",
            "details": "Public mosque near NUS."
        },
        {
            "name": "Hussain Sulaiman Mosque", 
            "lat": 1.2881, 
            "lon": 103.7842,
            "directions": "394 Pasir Panjang Rd, Singapore 118730.",
            "details": "Public mosque near NUS."
        },
        
        # Bukit Timah Campus
        {
            "name": "BTC Musollah", 
            "lat": 1.3194, 
            "lon": 103.8156,
            "directions": "Block B, Level 2. Located next to the Centre for Banking & Finance Law.",
            "details": "For safety and hygiene purposes, please bring your own prayer paraphernalia & use the prayer spaces responsibly."
        }
    ]
    
    # Find the closest location to the user
    closest = min(
        locations,
        key=lambda loc: geodesic((latitude, longitude), (loc["lat"], loc["lon"])).kilometers
    )
    
    # Calculate the distance
    distance = geodesic((latitude, longitude), (closest["lat"], closest["lon"])).kilometers
    
    await update.message.reply_text(
        f'<b>{closest["name"]}</b>\n'
        f'<b>Distance:</b> {distance:.2f} kilometers\n\n'
        f'<b>Directions:</b>\n{closest["directions"]}\n\n'
        f'<b>Additional Info:</b>\n{closest["details"]}',
        parse_mode=constants.ParseMode.HTML
    )

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get token from environment variable
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logging.error("Error: TELEGRAM_BOT_TOKEN environment variable not set")
        return
    
    # Start the health check server on port 8080
    health_server = start_health_server(port=8080)
    logging.info("Health check server started on port 8080 (endpoint: /ping)")
        
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("hello", hello))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.LOCATION, location_handler))

    logging.info("Starting Telegram bot...")
    
    try:
        app.run_polling()
    except KeyboardInterrupt:
        logging.info("Stopping application...")
        health_server.shutdown()

if __name__ == "__main__":
    main()
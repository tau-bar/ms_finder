from fastapi import FastAPI
from telegram_bot import main  # Import your bot's main function

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.on_event("startup")
async def start_bot():
    main()  # Start the bot polling when the server starts

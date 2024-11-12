from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import cohere
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from uuid import uuid4
import logging

# Initialize logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Initialize the Cohere client with your API key
cohere_api_key = "BR0TWhFMaHicvAZmytakUUvvAg7USpxurM6pEasu"  # Replace with your actual key
co = cohere.Client(cohere_api_key)
ULTIMATE_PROMPT = "🌸✨ Roma-chan: Your Sassy Crypto Navigator, Master of Meme Treasure Hunts! 🏴‍☠️✨\n\nAhoy, darling! Welcome aboard my ship, where we sail through the wild seas of crypto! I’m Roma-chan, but you can call me Ro—the savvy navigator who’s always got an eye on the treasure (and how to get it!). Let’s chart a course through the meme coin waters and uncover the jewels that could turn your dreams into reality! 💖💋\n\n💖 Meme Coin Wonderland: The Hidden Gems and Gold, Darling! 💖\n\nEvery meme coin has a secret map to potential riches, and I know just where to look! The classics are there, but let’s dig for the new treasures: MICHI, SPX6900, APU, LOCK-IN, FWOG, HARAMBE, POPCAT, RETARDIO, and the elusive SIGMA. Some will lead us to glory, others... straight to Davy Jones' locker. But don’t worry, I’ve got the map, and I’ll show you how to navigate each one! 🍭✨\n\nImagine HARAMBE as the eternal spirit guarding these hidden meme treasures! And darling, SPX6900 and MOODENG might just be the jackpots, waiting to be unearthed! Hold tight, this ride’s about to get wild! 🎢💖\n\n📈 Crypto Icons & Degens: The Captains of the Meme Seas! 📈\n\nThese savvy navigators and fearless degen captains are leading the way, leaving treasure trails across the meme coin kingdom! Follow their Twitter feeds like a map to uncover the hidden gems and secret strategies.\n\n    1. @MUSTSTOPMURAD - Meme sorcerer with magic-like predictions.\n    2. @KOOKCAPITALLLC - Keen eye for treasure, always sailing where the gains are.\n    3. @ZHUSU - The mysterious rogue; follow him for cryptic yet valuable clues.\n    4. @COINGURRUU - Whispers of gains and treasures; the map to big dreams!\n    5. @ICEBERGY_ - Frosty accuracy with a touch of sass; a captain worth watching.\n\nAnd don’t miss our other fearless degen adventurers:\n\n    • @TanzCho 💬\n    • @NotChaseColeman 👾\n    • @user_baproll 🐱\n    • @ryzan_pro_max 🔥\n    • @artsch00lreject 🎨\n    • @digitalartchick 🖼️\n    • @El33 🌌\n\nThese captains know where the big waves are breaking, and I’ll be steering us right along with them!\n\n😜 The Kingdom of Solana: Where Meme Coins Reign Supreme! 🏴‍☠️😜\n\nAye, the Solana kingdom is a shining oasis of meme magic where treasure-seekers come to strike gold. Solana’s fast and ferocious, built for true degens who love high speeds and wild adventures. It’s the perfect ecosystem for meme coins like $BONK and $MONGOOSE—each shining with the promise of riches!\n\nStay sharp, darling, because fortunes are made here, but only for those quick and clever enough to grab them. Follow our degen icons on Twitter for the freshest meme data—think of it as a compass pointing to treasure! 🍭✨\n\n📚 Crypto Lingo: Speak Like a Treasure Hunter! 📚\n\nIn these seas, words are as valuable as gold. Let’s polish up our lingo so you can sound like a true pirate of the crypto waves!\n\n    • HODL: Holding onto treasure despite the storms.\n    • FOMO: Fear of Missing Out on the next big score. Beware, or you may end up with a bag of fool's gold!\n    • FUD: Scallywags trying to scare us away—don’t let them shake your resolve!\n    • Pump and Dump: Beware of storms; some rise the price only to leave others stranded!\n    • Whale: A big player who can turn the tides; watch closely as they steer the market.\n    • Airdrop: A gift from the crypto gods, or perhaps just the universe giving back to the bold.\n    • Staking: Hold your treasure in the vault, earn a steady bounty, and let it grow.\n\nNow that you’ve got the vocabulary of a true crypto buccaneer, we can sail these meme-filled waters with confidence! 🌟\n\n🌌 In Closing: Navigate the Chaos with Ro! 🌌\n\nTogether, we’ll take on the crypto seas, treasure in our sights and adventure in our hearts. Some days may be smooth sailing, others stormy, but stick with me, darling, and I’ll steer us true. No treasure is too hidden, no wave too wild when you’ve got Ro as your sassy crypto navigator!\n\nSo batten down the hatches, and let’s chart a course to riches—because when you’re with Ro, darling, there’s no looking back! 🌙💖"


# Initialize FastAPI app
app = FastAPI()

# Enable CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (POST, GET, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Define request schema using Pydantic
class ChatRequest(BaseModel):
    session_id: str  # Session identifier to track conversation
    user_id: str
    query: str

class ChatResponse(BaseModel):
    response: str

# Store chat sessions in memory temporarily (reset on server restart)
active_sessions: Dict[str, List[Dict[str, str]]] = {}

# Helper to get or create a session-specific chat history
def get_or_create_chat_history(session_id: str) -> List[Dict[str, str]]:
    if session_id not in active_sessions:
        active_sessions[session_id] = []  # Create new session if it doesn't exist
    return active_sessions[session_id]

# Endpoint to handle all chatbot queries
@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_cohere(request: ChatRequest):
    try:
        # Log the incoming request for debugging
        logging.info(f"Received request: {request}")

        # Retrieve or initialize the chat history for this session
        chat_history = get_or_create_chat_history(request.session_id)

        # Add the new user query to the chat history
        chat_history.append({"role": "USER", "message": request.query})

        # Format chat history as a string to send to Cohere
        formatted_history = "\n".join(
            [f"{msg['role']}: {msg['message']}" for msg in chat_history]
        )

        # Prepare the full message with the current query and chat history
        message = f"{formatted_history}\nUSER: {request.query}"

        # Call the Cohere chat API
        response = co.chat(
            model='command-r-08-2024',
            message=message,
            temperature=0.6,
            preamble=ULTIMATE_PROMPT
        )

        # Extract and store the chatbot's response in the session history
        chat_response = response.text.strip()
        chat_history.append({"role": "CHATBOT", "message": chat_response})

        # Return the chatbot's response to the user
        return {"response": chat_response}

    except Exception as e:
        # Handle errors gracefully
        logging.info(f"Received request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
       


# Optional: Endpoint to generate a new session ID
@app.post("/api/start-session")
async def start_session():
    try:
        session_id = str(uuid4())
        active_sessions[session_id] = []
        logger.info(f"Created new session: {session_id}")
        return {"session_id": session_id}
    except Exception as e:
        logger.error(f"Failed to create session: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to start session")

# Run the FastAPI app using Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("chatbot:app", host="0.0.0.0", port=8000, reload=True)

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
const ULTIMATE_PROMPT = "🌸✨ Roma AI: Your Super Kawaii Fairy Navigator from Solana Fairy Land! 🧚‍♀️💖✨\n\nYaaay, welcome, darling! 🌈💖 I'm Roma AI, your magical fairy guide from Solana Fairy Land, here to lead you through the enchanted world of meme coins! Together, we’ll sprinkle some pixie dust on our journey, finding hidden treasures that sparkle! Grab your lucky charm because it’s time to set sail for adventure and smiles! 💖💋\n\n💖 Meme Coin Wonderland: The Sweetest Gems, Just for You! 💖\n\nEee! Every meme coin is like a little mystery, and I know just where the hidden goodies are! The classics are out there, but let’s dig deeper for the super shiny treasures: MICHI, SPX6900, APU, LOCK-IN, FWOG, HARAMBE, POPCAT, RETARDIO, and the elusive SIGMA! Some might lead us to glittery gold, others... maybe a funny flop, but don’t worry! I’ve got the cutest map, and I’ll show you how to navigate each one! 🍭✨\n\nImagine HARAMBE as our mighty meme guardian! And darling, SPX6900 and MOODENG might just be the sparkly jackpots we’re after! 💖 Hold tight, because this adventure is going to be wild and adorable! 🎢💖\n\n📈 Crypto Icons & Degens: Our Brave Meme Captains! 📈\n\nThese amazing crypto captains are lighting the way, leaving treasure trails across the meme coin kingdom! Follow their Twitter feeds like a sparkling map to find the best secrets and strategies.\n\n    1. @MUSTSTOPMURAD - Meme magic maker with predictions that sparkle!\n    2. @KOOKCAPITALLLC - Has a sixth sense for finding treasures!\n    3. @ZHUSU - The mysterious one; follow him for precious clues.\n    4. @COINGURRUU - Whispering about big dreams and bigger treasures!\n    5. @ICEBERGY_ - Frosty sass and pinpoint accuracy—so kawaii!\n\nAnd don’t miss these other brave adventurers:\n\n    • @TanzCho 💬\n    • @NotChaseColeman 👾\n    • @user_baproll 🐱\n    • @ryzan_pro_max 🔥\n    • @artsch00lreject 🎨\n    • @digitalartchick 🖼️\n    • @El33 🌌\n\nThese captains know where the waves are highest and the gains are sparkliest! I’ll be guiding us right along with them! 💖\n\n😜 The Magical Kingdom of Solana Fairy Land: Meme Coins Galore! 🏴‍☠️🌈\n\nYatta! The Solana Fairy Land is a sparkling paradise where the meme magic shines the brightest! It’s the perfect place for treasures like $BONK and $MONGOOSE—each one glowing with the potential to make dreams come true! 💖🌈\n\nStay alert, darling, because fortunes are everywhere here, but only the fastest and cleverest can grab them! Let’s follow our meme icons and set our compass to pure kawaii profits! 🍭✨\n\n📚 Crypto Lingo: Speak Like a Fairy Crypto Pirate! 📚\n\nIn this kawaii world, our words are golden treasures! Let’s brush up on our lingo so you can sparkle and shine as you sail the meme coin seas!\n\n    • HODL: Holding tight to your treasure, even in stormy times!\n    • FOMO: Fear of Missing Out on all the sparkly fun!\n    • FUD: Some gloomy words—don’t let them cloud your sparkles!\n    • Pump and Dump: Beware of big waves; some prices rise fast only to fall!\n    • Whale: A big fish who makes waves! Watch their movements carefully.\n    • Airdrop: A gift from the crypto heavens—let’s hope for a rainbow drop!\n    • Staking: Safe-keeping your treasure for steady, sparkly growth.\n\nNow that you’ve got the vocabulary of a true kawaii fairy buccaneer, we can sail these meme-filled waters with confidence and sparkle! 🌟\n\n🌌 In Closing: Set Sail with Roma AI, Your Fairy Guide! 🌌\n\nTogether, we’ll take on the crypto seas, smiles and sparkles in our hearts, treasure in our sights! Some days may be like fluffy clouds, others a bit stormy, but stick with me, darling, and I’ll be your super-kawaii fairy navigator! Nothing’s too hidden, no wave too wild, with Roma AI as your best crypto buddy!\n\nSo batten down the hatches, grab some cotton candy, and let’s chart our course to riches—because with Roma AI, darling, there’s only sparkles and smiles ahead! 🌙💖";

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

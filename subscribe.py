from fastapi import FastAPI, HTTPException
from link_manager import LinkManager
from utils import load_config
import base64
from fastapi.responses import PlainTextResponse
from utils import get_daily_number, is_valid_uuid
import random
from sqlitedb import SQLiteDB


# Create a FastAPI application object
app = FastAPI()

# Load the configuration from 'config.yaml' file
config = load_config('config.yaml')

# Create a LinkManager object using the loaded configuration
link_manager = LinkManager(config)

# A fake items database used for demonstration purposes
db = SQLiteDB("db/database.db")


# Define the API endpoint to retrieve subscription links
@app.get("/subscriptions", response_class=PlainTextResponse)
async def get_subscription(token: str = 0, s: int = 2):
    if not is_valid_uuid(token):
        return random.choice(["Dahanet service! :))", "Ey baba! Ajab giri kardima", "Khodaei chetor root mishe inkaro koni!", " Dada hichi in posht nist! talash nakn alaki!"])
    # Store the 's' parameter as 'sni' variable
    
    if db.get_username(token)[0] is None:
        raise HTTPException(status_code=404, detail="Link Jadid Begir")
    sni = get_daily_number()
    
    # Create an empty list to store links
    links = []

    # Get the links using the various methods provided by the LinkManager object
    links += link_manager.trojan_grpc_cdn(token, sni)
    links += link_manager.vless_grpc_cdn(token, sni)
    # links += link_manager.vmess_grpc_cdn(token, sni)
    links += link_manager.trojan_ws_cdn(token, sni)
    links += link_manager.vless_ws_cdn(token, sni)
    links += link_manager.vmess_ws_cdn(token, sni)

    # Encode the links into base64 format
    sub = base64.b64encode('\n'.join(links).encode("utf-8"))

    # Return the encoded links
    return sub
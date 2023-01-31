from fastapi import FastAPI
from link_manager import LinkManager
from utils import load_config
import base64
from fastapi.responses import PlainTextResponse
from utils import get_daily_number


# Create a FastAPI application object
app = FastAPI()

# Load the configuration from 'config.yaml' file
config = load_config('config.yaml')

# Create a LinkManager object using the loaded configuration
link_manager = LinkManager(config)

# A fake items database used for demonstration purposes
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


# Define the API endpoint to retrieve subscription links
@app.get("/subscriptions", response_class=PlainTextResponse)
async def get_subscription(token: str = 0, s: int = 2):
    # Store the 's' parameter as 'sni' variable
    sni = get_daily_number()
    
    # Create an empty list to store links
    links = []

    # Get the links using the various methods provided by the LinkManager object
    links += link_manager.trojan_grpc_cdn(token, sni)
    links += link_manager.vless_grpc_cdn(token, sni)
    links += link_manager.vmess_grpc_cdn(token, sni)
    links += link_manager.trojan_ws_cdn(token, sni)
    links += link_manager.vless_ws_cdn(token, sni)
    links += link_manager.vmess_ws_cdn(token, sni)

    # Encode the links into base64 format
    sub = base64.b64encode('\n'.join(links).encode("utf-8"))

    # Return the encoded links
    return sub
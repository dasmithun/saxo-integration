import os
from dotenv import load_dotenv

load_dotenv()

SIM_BASE    = "https://gateway.saxobank.com/sim/openapi"
TOKEN       = os.getenv("SAXO_SIM_TOKEN")
CLIENT_KEY  = os.getenv("SAXO_CLIENT_KEY")
ACCOUNT_KEY = os.getenv("SAXO_ACCOUNT_KEY")
APP_KEY     = os.getenv("SAXO_APP_KEY")
APP_SECRET  = os.getenv("SAXO_APP_SECRET")
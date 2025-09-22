import os
import json
from peer import start_peer  # tu función que levanta autenticación, servidor y menú

CONFIG_PATH = os.getenv("PEER_CONFIG", "/app/configs/default.json")

with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

# Inicializar directorio
directory = config["directory"]
if not os.path.exists(directory):
    os.makedirs(directory)

# Arrancar el peer
start_peer(
    peer_name=config["peer_name"],
    password=config["password"],
    directory=config["directory"],
    api_url=config["api_url"],
    peer_urls=config["peer_urls"],
    grpc_urls=config.get("grpc_urls", []),
    api_search_url=config["api_search_url"],
    peer_ip=config["ip"],
    peer_port=config["port"],
    peer_amigo_titular=config["peer_amigo_titular"],
    peer_amigo_suplente=config["peer_amigo_suplente"],
    auth_enabled=config.get("auth_enabled", True)
)

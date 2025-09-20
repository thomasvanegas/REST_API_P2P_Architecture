import json
from peer import run_menu
with open("/app/configs/peer1.json") as f:
    config = json.load(f)
run_menu(config["directory"], config["peer_urls"], config["api_search_url"])
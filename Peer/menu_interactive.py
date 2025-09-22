#!/usr/bin/env python3
"""
Script separado para menú interactivo del peer.
Se ejecuta cuando el usuario quiere usar el menú.
"""

import os
import json
import sys
from peer import menu, load_files

def main():
    # Cargar configuración
    config_path = os.getenv("PEER_CONFIG", "/app/configs/default.json")
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de configuración {config_path}")
        sys.exit(1)
    
    # Cargar archivos y mostrar menú
    files_index = load_files(
        config["directory"], 
        config["peer_urls"], 
        config.get("grpc_urls", [])
    )
    
    print(f"=== MENÚ INTERACTIVO - {config['peer_name']} ===")
    print(f"Directorio compartido: {config['directory']}")
    print(f"API Search URL: {config['api_search_url']}")
    print()
    
    menu(files_index, config["api_search_url"], config["directory"], config.get("grpc_urls", []))

if __name__ == "__main__":
    main()

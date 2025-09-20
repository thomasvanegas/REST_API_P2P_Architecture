import os
import json
import time
import multiprocessing as mp
import requests
from datetime import datetime

# --- Autenticación periódica ---
def auth_loop(peer_name, password, api_url, files_index, interval=60):
    loop = 0
    while True:
        loop += 1
        ts = datetime.now().isoformat(timespec='seconds')
        params = {
            "username": peer_name,
            "password": password,
            "files_index": json.dumps(files_index)
        }
        try:
            resp = requests.post(api_url, params=params, timeout=10)
            print(f"[{ts}] {peer_name} - intento #{loop} enviado (status={resp.status_code})")
        except Exception as e:
            print(f"[{ts}] {peer_name} - ERROR al enviar: {e}")
        time.sleep(interval)

# --- Cargar archivos del directorio compartido ---
def load_files(directory, peer_urls):
    files_index = []
    if not os.path.exists(directory):
        os.makedirs(directory)
    for fname in os.listdir(directory):
        fpath = os.path.join(directory, fname)
        if os.path.isfile(fpath):
            files_index.append({
                "namefile": fname,
                "url": [f"{peer}/{fname}" for peer in peer_urls]
            })
    return files_index

# --- Menú interactivo ---
def menu(files_index, api_search_url):
    while True:
        try:
            query = input("Nombre del archivo a buscar: ").strip()
            if not query:
                continue
            resp = requests.get(api_search_url, params={"filename": query}, timeout=5)
            print("Resultado de búsqueda:", resp.json())
        except Exception as e:
            print("Error buscando archivo:", e)

# --- Función principal del peer ---
def start_peer(peer_name, password, directory, api_url, peer_urls, api_search_url, peer_ip, peer_port, peer_amigo_titular, peer_amigo_suplente, auth_enabled):
    files_index = load_files(directory, peer_urls)
    auth_process = mp.Process(target=auth_loop, args=(peer_name, password, api_url, files_index))
    auth_process.start()
    menu(files_index, api_search_url)
    auth_process.join()

def run_menu(directory, peer_urls, api_search_url):
    files_index = load_files(directory, peer_urls)
    menu(files_index, api_search_url)

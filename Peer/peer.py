import os
import json
import time
import multiprocessing as mp
import requests
import random
import string
from datetime import datetime

# --- Autenticación periódica ---
def auth_loop(peer_name, password, api_url, files_index, interval=30):
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
def load_files(directory, peer_urls, self_url=None):
    files_index = []
    if not os.path.exists(directory):
        os.makedirs(directory)
    for fname in os.listdir(directory):
        fpath = os.path.join(directory, fname)
        if os.path.isfile(fpath):
            urls = []
            if self_url:
                urls.append(f"{self_url}/{fname}")
            files_index.append({
                "filename": fname,
                "url": urls
            })
    return files_index

# --- Menú interactivo ---
def menu(files_index, api_search_url):
    while True:
        print("\n--- MENÚ PEER ---")
        print("1. Descargar archivo")
        print("2. Subir archivo (próximamente)")
        print("0. Salir")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            try:
                query = input("Nombre del archivo a buscar: ").strip()
                if not query:
                    print("Debe ingresar un nombre de archivo.")
                    continue
                import requests
                resp = requests.get(api_search_url, params={"filename": query}, timeout=5)
                print("Resultado de búsqueda:", resp.json())
                # Aquí puedes implementar la lógica de descarga en el futuro
            except Exception as e:
                print("Error buscando archivo:", e)
        elif opcion == "2":
            print("Funcionalidad de subir archivo aún no implementada.")
        elif opcion == "0":
            print("Saliendo del menú.")
            break
        else:
            print("Opción no válida. Intente de nuevo.")

# --- Función principal del peer ---
def start_peer(peer_name, password, directory, api_url, peer_urls, api_search_url, peer_ip, peer_port, peer_amigo_titular, peer_amigo_suplente, auth_enabled):
    crear_archivos_aleatorios(directory)
    # Construye la URL del propio peer
    self_url = f"http://{peer_ip}:{peer_port}"
    files_index = load_files(directory, peer_urls, self_url=self_url)
    auth_process = mp.Process(target=auth_loop, args=(peer_name, password, api_url, files_index))
    auth_process.start()
    menu(files_index, api_search_url)
    auth_process.join()

def run_menu(directory, peer_urls, api_search_url):
    files_index = load_files(directory, peer_urls)
    menu(files_index, api_search_url)

def crear_archivos_aleatorios(directory, cantidad=3):
    if not os.path.exists(directory):
        os.makedirs(directory)
    for i in range(cantidad):
        nombre = f"archivo_{i+1}_{''.join(random.choices(string.ascii_lowercase, k=5))}.txt"
        ruta = os.path.join(directory, nombre)
        if not os.path.exists(ruta):  # No sobrescribir si ya existe
            with open(ruta, "w") as f:
                contenido = ''.join(random.choices(string.ascii_letters + string.digits, k=50))
                f.write(contenido)

import os
import json
import time
import multiprocessing as mp
import threading
import requests
from datetime import datetime

from grpc_server import serve_forever, start_grpc_server
from grpc_client import GrpcPeerClient

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
def load_files(directory, peer_urls, grpc_urls=None):
    files_index = []
    if not os.path.exists(directory):
        os.makedirs(directory)
    for fname in os.listdir(directory):
        fpath = os.path.join(directory, fname)
        if os.path.isfile(fpath):
            # No enviamos la dirección gRPC del propio peer al API
            files_index.append({
                "filename": fname,
                "url": []  # Lista vacía, el API no necesita saber cómo contactar a este peer
            })
    return files_index

# --- Menú interactivo ---
def menu(files_index, api_search_url, shared_directory, grpc_urls=None):
    while True:
        print("\n--- MENÚ PEER ---")
        print("1. Buscar y descargar archivo")
        print("2. Subir archivo (gRPC)")
        print("3. Listar archivos remotos (gRPC)")
        print("0. Salir")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            try:
                filename = input("Nombre del archivo a buscar: ").strip()
                if not filename:
                    print("Debe ingresar nombre del archivo.")
                    continue
                
                # Buscar archivo en la API
                import requests
                search_response = requests.get(f"{api_search_url}?filename={filename}")
                if search_response.status_code == 200:
                    data = search_response.json()
                    archivo = data.get("archivo")
                    disponibles = data.get("disponible_en", [])
                    
                    if not disponibles:
                        print(f"Archivo '{archivo}' no está disponible en ningún peer activo.")
                        continue
                    
                    print(f"\nArchivo encontrado: {archivo}")
                    print("Peers disponibles:")
                    
                    # Mapear peers a direcciones gRPC usando grpc_urls
                    peer_grpc_map = {}
                    if grpc_urls:
                        # Asumimos que el orden de grpc_urls corresponde al orden de peer_urls
                        for i, peer_url in enumerate(grpc_urls):
                            if i < len(disponibles):
                                peer_name = disponibles[i].get("peer")
                                peer_grpc_map[peer_name] = peer_url
                    
                    for i, peer_info in enumerate(disponibles, 1):
                        peer_name = peer_info.get("peer")
                        # Usar dirección gRPC si está disponible, sino usar la URL del API
                        peer_address = peer_grpc_map.get(peer_name, peer_info.get("url", "desconocido"))
                        print(f"{i}. Peer: {peer_name} - Dirección gRPC: {peer_address}")
                    
                    # Permitir selección
                    try:
                        choice = int(input("Seleccione peer para descargar (número): ").strip())
                        if 1 <= choice <= len(disponibles):
                            selected_peer = disponibles[choice - 1]
                            peer_name = selected_peer.get("peer")
                            # Usar dirección gRPC del mapeo
                            peer_address = peer_grpc_map.get(peer_name, selected_peer.get("url", "desconocido"))
                            
                            print(f"Descargando desde {peer_name} ({peer_address})...")
                            
                            # Descarga asíncrona en un hilo separado
                            import threading
                            def download_async():
                                try:
                                    client = GrpcPeerClient(peer_address)
                                    dest_path = os.path.join(shared_directory, archivo)
                                    with open(dest_path, "wb") as f:
                                        for data in client.download_file(archivo):
                                            f.write(data)
                                    print(f"✅ Archivo descargado exitosamente: {dest_path}")
                                except Exception as e:
                                    print(f"❌ Error al descargar: {e}")
                            
                            download_thread = threading.Thread(target=download_async)
                            download_thread.daemon = True
                            download_thread.start()
                            print("Descarga iniciada en segundo plano...")
                        else:
                            print("Selección inválida.")
                    except ValueError:
                        print("Debe ingresar un número válido.")
                else:
                    print(f"Error al buscar archivo: {search_response.status_code}")
            except Exception as e:
                print("Error al buscar archivo:", e)
        elif opcion == "2":
            try:
                target = input("Dirección del peer (ip:puerto) destino: ").strip()
                path = input("Ruta del archivo local a subir (desde el directorio compartido): ").strip()
                if not target or not path:
                    print("Debe ingresar peer y ruta del archivo.")
                    continue
                source_path = path if os.path.isabs(path) else os.path.join(shared_directory, path)
                if not os.path.isfile(source_path):
                    print("El archivo no existe:", source_path)
                    continue
                client = GrpcPeerClient(target)
                def chunks():
                    with open(source_path, "rb") as f:
                        while True:
                            data = f.read(1024 * 64)
                            if not data:
                                break
                            yield data
                filename = os.path.basename(source_path)
                resp = client.upload_file(filename, chunks())
                print("Resultado de subida:", resp.ok, resp.message)
            except Exception as e:
                print("Error al subir archivo:", e)
        elif opcion == "3":
            try:
                target = input("Dirección del peer (ip:puerto) a listar: ").strip()
                if not target:
                    print("Debe ingresar peer destino.")
                    continue
                client = GrpcPeerClient(target)
                resp = client.list_files()
                if not resp.files:
                    print("Sin archivos remotos.")
                else:
                    print("Archivos remotos:")
                    for fi in resp.files:
                        print(f"- {fi.filename} ({fi.size_bytes} bytes)")
            except Exception as e:
                print("Error al listar archivos:", e)
        elif opcion == "0":
            print("Saliendo del menú.")
            break
        else:
            print("Opción no válida. Intente de nuevo.")

# --- Función principal del peer ---
def start_peer(peer_name, password, directory, api_url, peer_urls, grpc_urls, api_search_url, peer_ip, peer_port, peer_amigo_titular, peer_amigo_suplente, auth_enabled):
    files_index = load_files(directory, peer_urls, grpc_urls)

    # Proceso 1: autenticación periódica
    auth_process = mp.Process(target=auth_loop, args=(peer_name, password, api_url, files_index))
    auth_process.daemon = True
    auth_process.start()

    # Proceso 2: servidor gRPC que permanece escuchando
    grpc_process = mp.Process(target=serve_forever, args=(directory, peer_ip, peer_port))
    grpc_process.daemon = True
    grpc_process.start()

    try:
        # Proceso principal: menú en hilo separado (no bloquea)
        menu_thread = threading.Thread(
            target=menu, 
            args=(files_index, api_search_url, directory, grpc_urls),
            daemon=True
        )
        menu_thread.start()
        
        # Mantener proceso principal vivo
        print(f"[{peer_name}] Servicios iniciados - Auth, gRPC Server y Menú funcionando")
        print(f"[{peer_name}] Para usar el menú: docker compose exec {peer_name.lower()} bash")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"[{peer_name}] Deteniendo servicios...")
    finally:
        # Al salir, terminar procesos hijos
        if grpc_process.is_alive():
            grpc_process.terminate()
            grpc_process.join(timeout=3)
        if auth_process.is_alive():
            auth_process.terminate()
            auth_process.join(timeout=3)

def run_menu(directory, peer_urls, grpc_urls, api_search_url):
    files_index = load_files(directory, peer_urls, grpc_urls)
    menu(files_index, api_search_url, shared_directory=directory, grpc_urls=grpc_urls)



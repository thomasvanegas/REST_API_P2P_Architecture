from fastapi import HTTPException, Query
from models import Peer
from datetime import datetime, timedelta
import json

# Simulación (RAM) de la base de datos
peers_list: list[dict] = [
    {"username": "Peer1", "password": "sd1234"},
    {"username": "Peer2", "password": "sd1234"},
    {"username": "Peer3", "password": "sd1234"},
    {"username": "Peer4", "password": "sd1234"}
]
peers_loggeados: dict[str, datetime] = {}
lista_archivos: list[dict] = []

def limpiar_peers_inactivos():
    """Elimina de la lista a los peers que no se han logueado en los últimos 2 minutos"""
    ahora = datetime.now()
    inactivos = [peer for peer, last_seen in peers_loggeados.items()
                 if ahora - last_seen > timedelta(minutes=2)]
    for peer in inactivos:
        del peers_loggeados[peer]
        print(f"[API] Peer '{peer}' se ha desconectado por inactividad ⛔")

def login_peer(username: str, password: str, files_index: str | None = Query(default=None, description="Lista JSON de archivos")
):
    for peer in peers_list:
        if peer["username"] == username and peer["password"] == password:
            nuevo_login = username not in peers_loggeados
            peers_loggeados[username] = datetime.now()
            limpiar_peers_inactivos()

            if nuevo_login:
                print(f"[API] Peer '{username}' se ha autenticado en la red ✅")

            # Procesar archivos enviados
            if files_index:
                try:
                    archivos = json.loads(files_index)
                    for archivo in archivos:
                        entry = {
                            "peer": username,
                            "filename": archivo.get("namefile"),
                            "url": archivo.get("url")
                        }
                        # Verifica si ya existe en la lista
                        ya_existe = any(
                            x["peer"] == entry["peer"] and
                            x["filename"] == entry["filename"] and
                            x["url"] == entry["url"]
                            for x in lista_archivos
                        )
                        if not ya_existe:
                            lista_archivos.append(entry)
                            print(f"[API] Peer '{username}' indexó archivo: {entry}")
                        else:
                            print(f"[API] Archivo ya indexado: {entry}")
                except json.JSONDecodeError:
                    raise HTTPException(status_code=400, detail="Formato inválido en files_index")
                
            return {"status": "OK", "token": "123abc"}

    raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")





'''
def crear_peer(peer: Peer) -> Peer:
    peers_list.append(peer.dict())
    return peer

def obtener_peers() -> list[dict]:
    return peers_list

def obtener_peer(username: str) -> dict:
    for peer in peers_list:
        if peer["username"] == username:
            return peer
    raise HTTPException(status_code=404, detail=f"El peer con username {username} no se encuentra en la base de datos")

def indexar_archivos(username: str, files: list[str]) -> dict:
    if username in peers_loggeados:
        lista_archivos.append({"username": username, "files": files})
        return {"status": "OK", "mensaje": f"Archivos indexados correctamente para el Peer {username}"}
    raise HTTPException(status_code=401, detail=f"El peer {username} no está loggeado")

def buscar_archivo(nombre_archivo: str) -> list[dict]:
    resultados_peers: list[str] = []
    resultados: list[dict] = []
    for elemento in lista_archivos:
        if nombre_archivo in elemento["files"]:
            resultados_peers.append(elemento["username"])
    if not resultados_peers:
        raise HTTPException(status_code=404, detail=f"El archivo {nombre_archivo} no se encuentra en la red de Peers")
    for peer in peers_list:
        if peer["username"] in resultados_peers:
            resultados.append({"username": peer["username"], "url": peer["url"]})
    return resultados
    '''
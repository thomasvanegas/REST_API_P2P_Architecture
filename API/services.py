from fastapi import HTTPException
from models import Peer

# Simulación (RAM) de la base de datos
peers_list: list[dict] = [
    {"username": "Peer1", "password": "sd1234", "url": "http://localhost:8001"},
    {"username": "Peer2", "password": "sd1234", "url": "http://localhost:8002"},
    {"username": "Peer3", "password": "sd1234", "url": "http://localhost:8003"}
]
peers_loggeados: list[str] = []
lista_archivos: list[dict] = []

def login_peer(username: str, password: str) -> dict:
    for peer in peers_list:
        if peer["username"] == username and peer["password"] == password:
            peers_loggeados.append(username)
            return {"status": "OK", "token": "123abc"}
    raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

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
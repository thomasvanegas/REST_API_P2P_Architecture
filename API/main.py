# Importacion de dependencias, librerias y modulos.
from fastapi import FastAPI, HTTPException
from typing import Union
from pydantic import BaseModel
from models import Peer

# Simulacion (RAM)de la base de datos para almacenar los usuarios.
peers_list: list[dict] = [
    {
        "username": "Peer1",
        "password": "sd1234",
        "url": "http://localhost:8001"
    },
    {
        "username": "Peer2",
        "password": "sd1234",
        "url": "http://localhost:8002"
    },
    {
        "username": "Peer3",
        "password": "sd1234",
        "url": "http://localhost:8003"
    }
]

# Lista de Peers conectados.
peers_loggeados: list[str] = []

# Lista de archivos por "Peer"
lista_archivos: list[dict] = []

# Instaciar la clase FastAPI
app = FastAPI()

# Definicion de la ruta "/", metodo GET
@app.get("/")
async def read_root() -> dict:
    return {"mensaje": "Hola Álvaro, este es un servidor P2P para la asignatura de Sistemas Distribuidos"}

# Login de un "Peer"
@app.post("login")
async def login(username: str, password: str) -> dict:
    for peer in peers_list:
        if peer["username"] == username and peer["password"] == password:
            peers_loggeados.append(username)
            return {"status": "OK", "token": "123abc"}
        else:
            raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

# Creacion de un nuevo "Peer" (usuario)
@app.post("/peers", response_model=Peer)
async def crear_usuario(peer: Peer)-> dict:
    peers_list.append(peer)
    return peer

# Obtener todos los "peers
@app.get("/peers", response_model=list[Peer])
async def obtener_peers()-> list[Peer]:
    return peers_list

#Obtener un "Peer" por su username.
@app.get("/peers/{username}", response_model=Peer)
async def obtener_peer(username: str) -> Peer:
    for peer in peers_list:
        if peer["username"] == username:
            return peer
        else:
            raise HTTPException(status_code=404, detail=f"El peer con username {username} no se encuentra en la base de datos")

# Indicar que archivos contiene un "Peer"
@app.post("/indexar")
async def indexar_peer(username: str, files: list[str]) -> dict:
    if username in peers_loggeados:
        lista_archivos.append({"username": username, "files": files})
        return {"status": "OK", "mensaje": f"Archivos indexados correctamente para el Peer {username}"}
    else:
        raise HTTPException(status_code=401, detail=f"El peer {username} no está loggeado")

# Buscar un archivo en la red de "Peers"
@app.get("/buscar")
def buscar_archivo(nombre_archivo: str) -> list[dict]:
    # Listas de control
    resultados_peers: list[str] = []
    resultados: list[dict] = []

    for elemento in lista_archivos:
        if nombre_archivo in elemento["files"]:
            resultados_peers.append(elemento["username"])
        else:
            raise HTTPException(status_code=404, detail=f"El archivo {nombre_archivo} no se encuentra en la red de Peers")
        

    for peer in peers_list:
        if peer["username"] in resultados_peers:
            resultados.append({"username": peer["username"], "url": peer["url"]})

    return resultados
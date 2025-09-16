# Importacion de dependencias, librerias y modulos.
from fastapi import FastAPI, HTTPException
from typing import Union
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

# Instaciar la clase FastAPI
app = FastAPI()

# Definicion de la ruta "/", metodo GET
@app.get("/")
async def read_root() -> dict:
    return {"mensaje": "Hola Álvaro, este es un servidor P2P para la asignatura de Sistemas Distribuidos"}

# Creacion de un nuevo "Peer" (usuario)
@app.post("/peers", response_model=Peer)
async def crear_usuario(peer: Peer)-> dict:
    peers_list.append(peer)
    return peer

@app.get("/peers", response_model=list[Peer])
async def obtener_usuarios() -> list[Peer]:
    return peers_list

@app.get("peers/{username}", response_model=Peer)
async def obtener_peer(username: str) -> Peer:
    for peer in peers_list:
        if peer["username"] == username:
            return peer
        else:
            raise HTTPException(status_code=404, detail=f"El peer con username {username} no se encuentra en la base de datos")
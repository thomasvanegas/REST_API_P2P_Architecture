from fastapi import APIRouter
from models import Peer
import services

router = APIRouter()

@router.get("/")
async def read_root():
    return {"mensaje": "Hola Álvaro, este es un servidor P2P para la asignatura de Sistemas Distribuidos"}

@router.post("/login")
async def login(username: str, password: str):
    return services.login_peer(username, password)

@router.post("/peers", response_model=Peer)
async def crear_usuario(peer: Peer):
    return services.crear_peer(peer)

@router.get("/peers")
async def obtener_peers():
    return services.obtener_peers()

@router.get("/peers/{username}", response_model=Peer)
async def obtener_peer(username: str):
    return services.obtener_peer(username)

@router.post("/indexar")
async def indexar_peer(username: str, files: list[str]):
    return services.indexar_archivos(username, files)

@router.get("/buscar")
async def buscar_archivo(nombre_archivo: str):
    return services.buscar_archivo(nombre_archivo)
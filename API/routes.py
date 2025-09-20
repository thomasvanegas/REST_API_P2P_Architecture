from fastapi import APIRouter, Query
from models import Peer
import services
from services import limpiar_peers_inactivos, peers_loggeados, lista_archivos

router = APIRouter()

@router.get("/")
async def read_root():
    return {"mensaje": "Hola Álvaro, este es un servidor P2P para la asignatura de Sistemas Distribuidos"}

@router.post("/login")
async def login(
    username: str,
    password: str,
    files_index: str = Query(default=None, description="Lista JSON de archivos")
) -> dict:
    return services.login_peer(username, password, files_index)

@router.get("/peers_activos")
def peers_activos():
    """Ver lista de peers logueados actualmente"""
    limpiar_peers_inactivos()
    return {"peers": list(peers_loggeados.keys())}


@router.get("/ver_archivos")
def obtener_archivos():
    """
    Devuelve la lista de archivos indexados por los peers autenticados.
    """
    limpiar_peers_inactivos()
    return {"archivos": lista_archivos}

'''

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
    '''
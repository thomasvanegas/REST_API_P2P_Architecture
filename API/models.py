"""
Definicion de los modelos (esquemas) de los datos.
Un modelo es una clase que define la estructura de los datos.
"""
from pydantic import BaseModel

# Definicion del modelo Peer.
class Peer(BaseModel):
    username: str
    password: str
    url: str # URL del "Peer" => Luego será la direción IP.
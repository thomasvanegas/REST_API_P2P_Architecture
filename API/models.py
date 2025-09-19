from pydantic import BaseModel

# Definicion del modelo Peer.
class Peer(BaseModel):
    username: str
    password: str
    url: str # URL del "Peer" => Luego será la direción IP.


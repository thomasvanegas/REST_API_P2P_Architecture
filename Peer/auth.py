import requests
import time

class PeerAuth:
    API_URL = "http://localhost:8000/login"

    peer_data = {
        "username": "Peer1",
        "password": "sd1234",
        #"url": "http://peer1.local"
    }

    while True:
        try:
            response = requests.post(API_URL, params={ 
                "username": peer_data["username"],
                "password": peer_data["password"]
            })
            print("Respuesta del servidor:", response.json())
        except Exception as e:
            print("Error conectando a la API:", e)
        
        time.sleep(60)  
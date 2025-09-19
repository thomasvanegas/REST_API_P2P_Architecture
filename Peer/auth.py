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

''' import os
    import time
    import requests

    API_URL = os.environ["API_URL"]

    peer_data = {
        "username": os.environ["PEER_NAME"],
        "password": os.environ["PEER_PASSWORD"],
        "url": os.environ["PEER_URL"],
    }

    while True:
        try:
            response = requests.post(
                API_URL,
                params={
                    "username": peer_data["username"],
                    "password": peer_data["password"]
                }
            )
            print(f"[{peer_data['username']}] Respuesta del servidor:", response.json())
        except Exception as e:
            print(f"[{peer_data['username']}] Error conectando a la API:", e)

        time.sleep(60)
 '''
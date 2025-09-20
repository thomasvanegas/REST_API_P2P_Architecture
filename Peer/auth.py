import requests
import time
import multiprocessing as mp
from datetime import datetime

class PeerAuth:
    import requests
import time
import multiprocessing as mp
from datetime import datetime
import json

class PeerAuth:

    API_URL = "http://localhost:8000/login"

    @staticmethod
    def peer_sender(name: str, username: str, files_index: list, interval: float,
                    initial_delay: float = 0.0, timeout: float = 10.0):
        """
        Función que ejecuta cada proceso 'peer'.
        - name: nombre del proceso (ej. "Peer1")
        - username: credencial de usuario a usar
        - files_index: lista de archivos del peer [{"namefile":"...","url":"..."}, ...]
        - interval: segundos entre envíos
        - initial_delay: retardo antes del primer envío
        - timeout: timeout para requests
        """

        if initial_delay > 0:
            time.sleep(initial_delay)

        loop = 0
        while True:
            loop += 1
            ts = datetime.now().isoformat(timespec='seconds')

            # Si es Peer3, después de 2 envíos, pausa 3 minutos y luego sigue normalmente
            if name == "Peer3" and loop == 2:
                print(f"[{ts}] {name} - Pausando autenticación por 3 minutos...")
                time.sleep(180)  # 3 minutos
                print(f"[{datetime.now().isoformat(timespec='seconds')}] {name} - Reanudando autenticación.")

            try:
                # Construir parámetros (query params) con credenciales + files_index
                params = {
                    "username": username,
                    "password": "sd1234",
                    "files_index": json.dumps(files_index)  # mandamos la lista como string JSON
                }

                resp = requests.post(PeerAuth.API_URL, params=params, timeout=timeout)

                sent_msg = f"[{ts}] {name} - intento #{loop}: mensaje ENVIADO (status={resp.status_code})"
                try:
                    content = resp.json()
                except ValueError:
                    content = resp.text

                print(sent_msg)
                print(f"    enviado files_index: {params['files_index']}")
                print(f"    respuesta: {content}")

            except requests.exceptions.RequestException as e:
                err_ts = datetime.now().isoformat(timespec='seconds')
                print(f"[{err_ts}] {name} - intento #{loop}: ERROR al enviar -> {e}")

            time.sleep(interval)


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
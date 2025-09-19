import time
import multiprocessing as mp
from datetime import datetime
from auth import PeerAuth

def main():
    # Configuración de 3 procesos: Peer1, Peer2, Peer3 con usernames distintos
    configs = [
        ("Peer1", "Peer1", 5.0, 0.0),
        ("Peer2", "Peer2", 7.0, 1.5),
        ("Peer3", "Peer3", 11.0, 0.8),
    ]

    processes = []
    for name, username, interval, initial_delay in configs:
        p = mp.Process(target=PeerAuth.peer_sender, args=(name, username, interval, initial_delay), daemon=True)
        p.start()
        processes.append(p)
        print(f"[{datetime.now().isoformat(timespec='seconds')}] Lanzado proceso {name} con usuario={username} (interval={interval}s, delay={initial_delay}s)")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDeteniendo procesos...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.join(timeout=2)
        print("Todos los procesos finalizados.")

'''
def main():
    peer_auth = auth.PeerAuth()
    peer_auth.run()  
'''

if __name__ == "__main__":
    main()
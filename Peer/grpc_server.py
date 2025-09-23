"""Servidor gRPC que expone operaciones de intercambio de archivos entre peers.

Este módulo implementa la clase `PeerService`, un `Servicer` generado por gRPC,
que ofrece tres RPCs:
  - ListFiles: lista los archivos disponibles en un directorio compartido.
  - DownloadFile: transmite un archivo como flujo de chunks.
  - UploadFile: recibe un flujo de chunks para escribir un archivo en disco.

La lógica existente se mantiene intacta. Solo se agregan comentarios y
docstrings para mejorar la comprensión y el mantenimiento.
"""

import os
import grpc
from concurrent import futures
from typing import Iterator

from generated import peer_pb2
from generated import peer_pb2_grpc


class PeerService(peer_pb2_grpc.PeerServiceServicer):
    """Implementación del servicio gRPC para un peer de archivos.

    Parámetros:
        shared_directory: Ruta del directorio donde se listan, leen y escriben
            archivos compartidos por el peer.
    """

    def __init__(self, shared_directory: str) -> None:
        self.shared_directory = shared_directory

    def ListFiles(self, request, context):  # type: ignore[override]
        """Retorna metadatos de los archivos presentes en el directorio compartido."""
        files = []
        if os.path.isdir(self.shared_directory):
            for fname in os.listdir(self.shared_directory):
                fpath = os.path.join(self.shared_directory, fname)
                if os.path.isfile(fpath):
                    size_bytes = os.path.getsize(fpath)
                    files.append(peer_pb2.FileInfo(filename=fname, size_bytes=size_bytes))
        return peer_pb2.ListFilesResponse(files=files)

    def DownloadFile(self, request, context) -> Iterator[peer_pb2.Chunk]:  # type: ignore[override]
        """Transmite el contenido del archivo solicitado en chunks de tamaño fijo."""
        filename = request.filename
        fpath = os.path.join(self.shared_directory, filename)
        if not os.path.isfile(fpath):
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Archivo no encontrado")
            return
        try:
            with open(fpath, "rb") as f:
                while True:
                    data = f.read(1024 * 64)
                    if not data:
                        break
                    yield peer_pb2.Chunk(data=data)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

    def UploadFile(self, request_iterator, context):  # type: ignore[override]
        """Recibe un stream de chunks y los escribe en un archivo destino.

        Si el primer chunk incluye `filename`, se usa dicho nombre; de lo contrario
        se emplea un nombre por defecto. Los datos se escriben secuencialmente.
        """
        filename = None
        f = None
        written = 0
        try:
            for chunk in request_iterator:
                if filename is None:
                    # El primer chunk debe traer filename en metadata; si no, usar request field
                    filename = getattr(chunk, "filename", None) or getattr(chunk, "name", None)
                    if filename is None and hasattr(chunk, "data") and written == 0:
                        filename = "upload.bin"
                if f is None:
                    if filename is None:
                        filename = "upload.bin"
                    os.makedirs(self.shared_directory, exist_ok=True)
                    fpath = os.path.join(self.shared_directory, filename)
                    f = open(fpath, "wb")
                if chunk.data:
                    f.write(chunk.data)
                    written += len(chunk.data)
            if f is not None:
                f.flush()
                f.close()
            return peer_pb2.UploadResponse(ok=True, message=f"Escrito {written} bytes en {filename}")
        except Exception as e:
            if f is not None:
                f.close()
            return peer_pb2.UploadResponse(ok=False, message=str(e))


def start_grpc_server(shared_directory: str, host: str = "0.0.0.0", port: int = 8001):
    """Inicializa y arranca el servidor gRPC del peer.

    Returns:
        Instancia de servidor gRPC ya iniciada.
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    peer_pb2_grpc.add_PeerServiceServicer_to_server(PeerService(shared_directory), server)
    server.add_insecure_port(f"{host}:{port}")
    server.start()
    return server


def serve_forever(shared_directory: str, host: str = "0.0.0.0", port: int = 8001):
    """Bloquea el hilo principal esperando la terminación del servidor."""
    server = start_grpc_server(shared_directory=shared_directory, host=host, port=port)
    server.wait_for_termination()



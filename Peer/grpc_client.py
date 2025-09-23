"""Cliente gRPC para interactuar con el servicio de peers.

Este módulo expone una clase de alto nivel `GrpcPeerClient` que encapsula
las llamadas remotas definidas en el servicio gRPC (listar, descargar y
subir archivos). No modifica la lógica de negocio; únicamente añade
documentación para facilitar el mantenimiento y el uso del cliente.
"""

import grpc
from typing import Iterable, Iterator

from generated import peer_pb2
from generated import peer_pb2_grpc


class GrpcPeerClient:
    """Proveedor de métodos cliente para el `PeerService` gRPC.

    Atributos:
        channel: Canal gRPC inseguro a la dirección de destino.
        stub: Stub generado para invocar RPCs del servicio `PeerService`.

    Parámetros:
        target: Dirección del peer en formato "host:puerto" (p. ej.,
            "127.0.0.1:8001").
    """

    def __init__(self, target: str) -> None:
        # Ejemplo de destino: "127.0.0.1:8001"
        self.channel = grpc.insecure_channel(target)
        self.stub = peer_pb2_grpc.PeerServiceStub(self.channel)

    def list_files(self) -> peer_pb2.ListFilesResponse:
        """Obtiene el listado de archivos compartidos en el peer remoto.

        Returns:
            Respuesta `ListFilesResponse` con la colección de `FileInfo`.
        """
        return self.stub.ListFiles(peer_pb2.Empty())

    def download_file(self, filename: str) -> Iterator[bytes]:
        """Descarga un archivo remoto como flujo de bytes.

        Parámetros:
            filename: Nombre del archivo a descargar.

        Yields:
            Chunks de bytes con los datos del archivo.
        """
        stream = self.stub.DownloadFile(peer_pb2.DownloadRequest(filename=filename))
        for chunk in stream:
            # Cada mensaje del stream incluye un campo `data` con el fragmento
            yield chunk.data

    def upload_file(self, filename: str, data_iter: Iterable[bytes]) -> peer_pb2.UploadResponse:
        """Sube un archivo al peer remoto usando streaming de chunks.

        Parámetros:
            filename: Nombre con el que se almacenará el archivo en el peer.
            data_iter: Iterable de bytes que produce los chunks a enviar.

        Returns:
            `UploadResponse` con el resultado de la operación.
        """

        def gen():
            # El primer chunk incluye `filename` (si la definición proto lo permite)
            first = True
            for data in data_iter:
                if first:
                    yield peer_pb2.UploadChunk(filename=filename, data=data)
                    first = False
                else:
                    yield peer_pb2.UploadChunk(data=data)

        return self.stub.UploadFile(gen())



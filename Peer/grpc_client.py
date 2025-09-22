import grpc
from typing import Iterable, Iterator

from generated import peer_pb2
from generated import peer_pb2_grpc


class GrpcPeerClient:
    def __init__(self, target: str) -> None:
        # target example: "127.0.0.1:8001"
        self.channel = grpc.insecure_channel(target)
        self.stub = peer_pb2_grpc.PeerServiceStub(self.channel)

    def list_files(self) -> peer_pb2.ListFilesResponse:
        return self.stub.ListFiles(peer_pb2.Empty())

    def download_file(self, filename: str) -> Iterator[bytes]:
        stream = self.stub.DownloadFile(peer_pb2.DownloadRequest(filename=filename))
        for chunk in stream:
            yield chunk.data

    def upload_file(self, filename: str, data_iter: Iterable[bytes]) -> peer_pb2.UploadResponse:
        def gen():
            first = True
            for data in data_iter:
                if first:
                    # Enviar primer chunk con nombre si el proto lo soporta
                    yield peer_pb2.UploadChunk(filename=filename, data=data)
                    first = False
                else:
                    yield peer_pb2.UploadChunk(data=data)
        return self.stub.UploadFile(gen())



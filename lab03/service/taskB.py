import argparse
import socket
import threading
from pathlib import Path

ROOTDIR = Path("./files")

HEADER_TEMPLATE = """HTTP/1.1 {}
Content-Type: {}
Content-Length: {}

"""


def build_response(status: str, content_type: str, content: bytes) -> bytes:
    return HEADER_TEMPLATE.format(status, content_type, len(content)).encode(encoding="ascii") + content


def handle_request(client_socket):
    request = client_socket.recv(1024).decode()

    try:
        method, path, proto = request.splitlines()[0].split()
        filename = path.split("/")[1]
        print(f"Requested file: {filename}")
        filepath = ROOTDIR / Path(filename)

        if method != "GET":
            response = build_response("405 Method Not Allowed", "text/plain", b"405 Method Not Allowed")
        elif filepath.exists() and (filepath.is_file() or filepath.is_fifo()):
            with filepath.open("rb") as f:
                response = build_response("200 OK", "text/plain", f.read())
        else:
            response = build_response("404 Not Found", "text/plain", b"404 Not Found")

        client_socket.sendall(response)
    finally:
        client_socket.close()


def start(host: str, port: int):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Listening on http://{host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Accepted connection from {addr}")
        thread = threading.Thread(target=handle_request, args=(client_socket,))
        thread.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser("File Server")
    parser.add_argument("port", type=int)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    args = parser.parse_args()
    start(args.host, args.port)

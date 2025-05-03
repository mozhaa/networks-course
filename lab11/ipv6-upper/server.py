import socket
import argparse


def main(host: str, port: int) -> None:
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as sock:
        sock.bind((host, port))
        sock.listen()
        print(f"Listening on {host}:{port}")

        while True:
            client_socket, client_address = sock.accept()
            with client_socket:
                print(f"Connected to {client_address}")
                data = client_socket.recv(1024)
                if not data:
                    break
                print(f"{client_address[0]}:{client_address[1]} sent {data}")
                client_socket.sendall(data.decode().upper().encode())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="::1")
    parser.add_argument("--port", type=int, default="12345")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args.host, args.port)

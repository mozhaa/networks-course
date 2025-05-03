import socket
import argparse


def main(host: str, port: int) -> None:
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        sock.sendall(input("Input message: ").encode())
        print(f"Server response: {sock.recv(1024).decode()}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="::1")
    parser.add_argument("--port", type=int, default="12345")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args.host, args.port)

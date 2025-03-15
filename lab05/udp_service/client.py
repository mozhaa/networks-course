import argparse
import socket


def start_client(port: int):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client_socket.bind(("", port))

    print(f"client start on port={port}...")
    while True:
        data, addr = client_socket.recvfrom(1024)
        print(f'server ({addr}) message: "{data.decode()}"')


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int, default=8080)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    start_client(args.port)

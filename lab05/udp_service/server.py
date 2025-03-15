import argparse
import socket
import time
from datetime import datetime


def start_server(port: int):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    print(f"server start sending to port={port}...")
    while True:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        server_socket.sendto(current_time.encode(), ("255.255.255.255", port))
        time.sleep(1)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("broadcast_port", type=int, default=8080, help="messages will be sent on this port")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    start_server(args.broadcast_port)

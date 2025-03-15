import argparse
import socket


def start_client(host: str, port: int) -> None:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    while True:
        command = input("$: ")
        client_socket.sendall(command.encode(encoding="utf-8"))

        if command.lower() == "exit":
            break

        output = client_socket.recv(4096).decode(encoding="utf-8")
        print(output, end="")

    client_socket.close()


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("host", type=str, default="localhost")
    parser.add_argument("port", type=int, default=8080)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    start_client(args.host, args.port)

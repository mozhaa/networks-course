import argparse
import socket
import sys

REQUEST_TEMPLATE = """GET /{} HTTP/1.1
Host: localhost
Connection: close

"""


def build_request(filename: str) -> bytes:
    return REQUEST_TEMPLATE.format(filename).encode(encoding="ascii")


def get_status_code(response: str) -> int:
    return int(response.splitlines()[0].split()[1])


def get_content(response: str) -> str:
    lines = response.splitlines()
    content_start = lines.index("") + 1
    return "\n".join(lines[content_start:])


def main(host, port, filename):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        client_socket.sendall(build_request(filename))

        response = b""
        while True:
            part = client_socket.recv(4096)
            if not part:
                break
            response += part

        response = response.decode("utf-8")
        status_code = get_status_code(response)
        if status_code != 200:
            print(response)
            sys.exit(1)
        else:
            print(get_content(response))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Client for File Server")
    parser.add_argument("host", type=str)
    parser.add_argument("port", type=int)
    parser.add_argument("filename", type=str)
    args = parser.parse_args()

    main(args.host, args.port, args.filename)

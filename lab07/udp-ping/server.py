import socket
import random
import argparse
import logging
import signal
import os

logger = logging.getLogger("udp-ping-server")


def start_server(host: str, port: int) -> None:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    server_socket.settimeout(1.0)
    setup_interrupt_handler(server_socket)
    print(f"listening on {host}:{port}")

    while True:
        try:
            message, client_address = server_socket.recvfrom(1024)
        except socket.timeout:
            continue
        if not message:
            return

        message_str = message.decode(encoding="utf-8")
        logger.info(f"received message from client: {message_str}")

        if random.random() < 0.2:
            logger.info("dropped package")
            continue

        message_str = message_str.upper()
        server_socket.sendto(message_str.encode(encoding="utf-8"), client_address)
        logger.info(f"responded to client: {message_str}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser("udp-ping client")
    parser.add_argument("host", type=str, default="127.0.0.1", help="server host")
    parser.add_argument("port", type=int, default=12000, help="server port")
    return parser.parse_args()


def setup_logger() -> None:
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    logger.addHandler(console_handler)


def setup_interrupt_handler(s: socket.socket) -> None:
    def create_handler(obj):
        def _handler(signum, frame):
            print("interrupted. exiting...")
            obj.close()
            signal.signal(signum, signal.SIG_DFL)
            os.kill(os.getpid(), signum)

        return _handler

    signal.signal(signal.SIGINT, create_handler(s))


if __name__ == "__main__":
    setup_logger()
    args = parse_args()
    start_server(args.host, args.port)

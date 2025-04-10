import socket
import argparse
import bencodepy
import signal
import os
from proto import send_data, receive_data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("host", type=str, help="server host")
    parser.add_argument("port", type=int, help="server port")
    parser.add_argument("filename", type=str, help="file")
    parser.add_argument(
        "--action", type=str, choices=["send", "receive"], default="receive", help="action to do with file"
    )
    parser.add_argument("--timeout", type=float, default=1, help="socket timeout for sending")
    return parser.parse_args()


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
    args = parse_args()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.host, args.port))
    setup_interrupt_handler(sock)
    if args.action == "send":
        client_addr, client_port = bencodepy.decode(receive_data(sock))
        with open(args.filename, "rb") as f:
            send_data(sock, f.read(), (client_addr.decode(), client_port), args.timeout)
    else:
        with open(args.filename, "wb") as f:
            f.write(receive_data(sock))

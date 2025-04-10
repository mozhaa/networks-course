import socket
import argparse
import bencodepy
import signal
import os
from proto import send_data, receive_data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str, help="file")
    parser.add_argument("server_host", type=str, help="server host")
    parser.add_argument("server_port", type=int, help="server port")
    parser.add_argument(
        "--action", type=str, choices=["send", "receive"], default="send", help="action to do with file"
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
    server_addr = (args.server_host, args.server_port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 0))
    setup_interrupt_handler(sock)
    if args.action == "send":
        with open(args.filename, "rb") as f:
            send_data(sock, f.read(), server_addr, args.timeout)
    else:
        send_data(sock, bencodepy.encode(sock.getsockname(), encoding="ascii"), server_addr, args.timeout)
        with open(args.filename, "wb") as f:
            f.write(receive_data(sock))

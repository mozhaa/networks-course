import socket
import time
import argparse


def start_client(host: str, port: int) -> None:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    interval = 1.0
    client_socket.settimeout(interval)

    for sequence_number in range(1, 11):
        message = f"Ping {sequence_number} {time.time()}".encode(encoding="utf-8")
        client_socket.sendto(message, (host, port))
        start_time = time.time()

        try:
            response_message, _ = client_socket.recvfrom(1024)
            rtt = time.time() - start_time
            print(f"{response_message.decode(encoding="utf-8")} RTT: {rtt:.6f} s")
            time.sleep(interval - rtt)
        except socket.timeout:
            print("Request timed out")
        except ConnectionResetError:
            print("Disconnected from server")
            return


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser("udp-ping client")
    parser.add_argument("host", type=str, default="127.0.0.1", help="server host")
    parser.add_argument("port", type=int, default=12000, help="server port")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    start_client(args.host, args.port)

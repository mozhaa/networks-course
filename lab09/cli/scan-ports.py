import socket
import argparse
from typing import List


def scan_port(ip: str, port: int, timeout: float) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    result = sock.connect_ex((ip, port))
    sock.close()
    return result == 0


def scan_ports(ip: str, start_port: int, end_port: int, timeout: float, verbose: bool) -> List[int]:
    ports = []
    for port in range(start_port, end_port + 1):
        if verbose:
            print(f"Scanning port {port}...", end=" ")
        status = scan_port(ip, port, timeout)
        if verbose:
            print("success" if status else "failed")
        if status:
            ports.append(port)
    return ports


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan ports of host.")
    parser.add_argument("ip", type=str, help="ip-address of host")
    parser.add_argument("start_port", type=int, help="port range start")
    parser.add_argument("end_port", type=int, help="port range end")
    parser.add_argument("-t", "--timeout", type=float, default=0.5, help="timeout for checking port")
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose mode")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.start_port < 0 or args.end_port > 65535 or args.start_port > args.end_port:
        raise ValueError("invalid port range")

    ports = scan_ports(args.ip, args.start_port, args.end_port, args.timeout, args.verbose)
    if len(ports) > 0:
        print(f"Available ports on {args.ip}:")
        for port in ports:
            print(port)
    else:
        print(f"No available ports in range {args.start_port}-{args.end_port} was found")

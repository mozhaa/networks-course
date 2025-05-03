import socket
import argparse
import os
import time
import struct
import sys


ICMP_ECHO_REQUEST = 8
ICMP_TIME_EXCEEDED = 11
ICMP_ECHO_REPLY = 0


def checksum(data: bytes) -> int:
    if len(data) % 2 != 0:
        data += b"\0"
    s = sum(struct.unpack("!%sH" % (len(data) // 2,), data))
    s = (s >> 16) + (s & 0xFFFF)
    s = ~s & 0xFFFF
    return s


def create_packet(id_: int) -> bytes:
    data = b"BCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwx"
    header = struct.pack("!BBHHH", ICMP_ECHO_REQUEST, 0, 0, id_, 0)
    header = struct.pack("!BBHHH", ICMP_ECHO_REQUEST, 0, checksum(header + data), id_, 0)
    return header + data


def traceroute(host, max_hops: int = 30, n_retries: int = 5, timeout: float = 1) -> None:
    host_ip = socket.gethostbyname(host)
    print(f"Traceroute to {host} [{host_ip}]")

    with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp")) as sock:
        done = False
        for ttl in range(1, max_hops + 1):
            if done:
                break
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
            sock.settimeout(timeout)

            packet_id = os.getpid() & 0xFFFF
            packet = create_packet(packet_id)

            router_ip = None
            rtts = []
            print(str(ttl).rjust(3), end="")

            for i in range(n_retries):
                start_time = time.time()
                rtt = None
                
                sock.sendto(packet, (host_ip, 1))
                try:
                    data, addr = sock.recvfrom(1024)
                    router_ip = router_ip or addr[0]

                    rtt = 1000 * (time.time() - start_time)
                    rtts.append(rtt)
                    if data[20] == ICMP_ECHO_REPLY:
                        done = True
                except TimeoutError:
                    pass

                c = f"{int(rtt)}ms" if rtt is not None else "*"
                print(c.rjust(6), end="")

            if len(rtts) > 0:
                print(f"[{int(sum(rtts)/len(rtts))}ms]".rjust(10), end="")

            if router_ip is not None:
                print(" - ", end="")
                try:
                    hostname = socket.gethostbyaddr(router_ip)[0]
                    print(f"{hostname} [{router_ip}]")
                except socket.herror:
                    print(router_ip)
            else:
                print()
            
            sys.stdout.flush()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("host", type=str, help="host to traceroute")
    parser.add_argument("--max-hops", type=int, default=30, help="max ttl to try")
    parser.add_argument("--retries", type=int, default=3, help="retries of one specific ttl")
    parser.add_argument("--timeout", type=float, default=1, help="timeout for one reply")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    traceroute(args.host, args.max_hops, args.retries, args.timeout)

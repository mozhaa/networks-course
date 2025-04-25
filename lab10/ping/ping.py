import os
import socket
import struct
import time
import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ping a host using ICMP echo requests")
    parser.add_argument("host", type=str, help="host to ping")
    parser.add_argument("-n", type=int, default=-1, help="number of packets to send")
    parser.add_argument("-s", type=int, default=32, help="packet size")
    parser.add_argument("-i", type=float, default=1, help="interval between packets")
    return parser.parse_args()


def checksum(data: bytes) -> int:
    if len(data) % 2 != 0:
        data += b"\0"
    s = sum(struct.unpack("!%sH" % (len(data) // 2,), data))
    s = (s >> 16) + (s & 0xFFFF)
    s = ~s & 0xFFFF
    return s


def create_packet(id_: int, packet_size: int) -> bytes:
    time_stamp = int(time.time() * 1000)
    data = bytearray(packet_size)
    struct.pack_into("d", data, 0, time_stamp)

    header = struct.pack("!BBHHH", 8, 0, 0, id_, 0)
    header = struct.pack("!BBHHH", 8, 0, checksum(header + data), id_, 0)

    return header + data


def ping(host: str, n_packets: int, packet_size: int, interval: float) -> None:
    icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
    icmp_socket.settimeout(1)

    packet = create_packet(os.getpid() & 0xFFFF, packet_size)

    rtts = []
    n_lost_packets = 0

    print(f"Pinging {host} with {packet_size} bytes of data:")

    i = 0
    while i != n_packets:
        start_time = time.time()
        icmp_socket.sendto(packet, (host, 1))

        try:
            icmp_socket.recvfrom(1024)
            rtt = (time.time() - start_time) * 1000
            rtts.append(rtt)
            print(f"Reply from {host}: time={int(rtt)}ms")
        except socket.timeout:
            print("Request timed out.")
            n_lost_packets += 1

        time.sleep(interval)
        i += 1

    icmp_socket.close()

    print(f"Ping statistics for {host}:")
    print(
        f"\tPackets: Sent = {n_packets}, Received = {n_packets - n_lost_packets},",
        f"Lost = {n_lost_packets} ({n_lost_packets / n_packets:.0%} loss)",
    )
    if len(rtts) > 0:
        print("Approximate round trip times in milli-seconds:")
        print(f"\tMinimum = {min(rtts):.0f}ms, Maximum = {max(rtts):.0f}ms, Average = {sum(rtts)/len(rtts):.0f}ms")


if __name__ == "__main__":
    args = parse_args()
    ping(args.host, args.n, args.s, args.i)

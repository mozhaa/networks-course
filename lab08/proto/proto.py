import socket
import bencodepy
import itertools
import random
from typing import Optional
from checksum import verify_checksum, calculate_checksum


class packet:
    def __init__(self, framenumber: int, data: bytes | list, checksum: Optional[int] = None) -> None:
        self.framenumber = framenumber
        self.data = bytes(data)
        self.checksum = checksum or calculate_checksum(data)

    def encode(self) -> bytes:
        return bencodepy.encode(
            [
                self.framenumber,
                self.data,
                self.checksum,
            ]
        )

    @classmethod
    def decode(cls, encoded: bytes) -> "packet":
        return cls(*bencodepy.decode(encoded))

    @property
    def valid(self) -> bool:
        return verify_checksum(self.data, self.checksum)


def is_packet_lost() -> bool:
    return random.random() < 0.3


end_sequence = b"END123"


def receive_data(sock: socket.socket) -> bytes:
    framenumber = 0
    result = b""
    while True:
        try:
            data, addr = sock.recvfrom(2048)
        except socket.timeout:
            continue
        except WindowsError as e:
            print(e)
            print("exiting...")
            return
        except Exception as e:
            print(f"[WARNING]: {e}")
            continue
        if is_packet_lost():
            continue
        if not data:
            break
        pkt = packet.decode(data)
        if pkt.valid:
            if pkt.framenumber == framenumber:
                sock.sendto(framenumber.to_bytes(length=1), addr)
                if pkt.data == end_sequence:
                    break
                result += pkt.data
                framenumber = 1 - framenumber
        else:
            sock.sendto((1 - pkt.framenumber).to_bytes(length=1), addr)
    return result


def send_data(sock: socket.socket, data: bytes, addr: str, timeout: float) -> None:
    framenumber = 0
    for pdata in itertools.chain(itertools.batched(data, 1024), [end_sequence]):
        pkt = packet(framenumber, pdata)
        while True:
            sock.sendto(pkt.encode(), addr)
            sock.settimeout(timeout)
            try:
                ack, _ = sock.recvfrom(1024)
                if int.from_bytes(ack) == framenumber:
                    framenumber = 1 - framenumber
                    break
            except socket.timeout:
                continue
            except WindowsError as e:
                print(e)
                print("exiting...")
                return
            except Exception as e:
                print(f"[WARNING]: {e}")
                continue
    sock.sendto(end_sequence, addr)

import binascii
import random
from typing import Tuple


def crc32(data: bytes) -> int:
    return binascii.crc32(data) & 0xFFFFFFFF


def generate_packet(data: bytes) -> Tuple[bytes, int]:
    crc = crc32(data)
    return data, crc


def introduce_error(data: bytes) -> bytes:
    data = bytearray(data)
    if len(data) == 0:
        return
    bit_to_flip = random.randint(0, len(data) * 8 - 1)
    byte_index = bit_to_flip // 8
    bit_index = bit_to_flip % 8
    data[byte_index] ^= 1 << bit_index
    return bytes(data)


def check_packet(data: bytes, crc: int) -> bool:
    return crc32(data) == crc


def main() -> None:
    text = input("Enter text: ")
    packet_size = 5
    packets = [text[i : i + packet_size].encode("utf-8") for i in range(0, len(text), packet_size)]

    for i, packet in enumerate(packets):
        data, crc = generate_packet(packet)

        choice = random.choice([True, False])
        if choice:
            data = introduce_error(data)

        is_valid = check_packet(data, crc)
        assert is_valid != choice

        print(f'Packet: "{data}", Checksum: {crc}')
        is_valid = check_packet(data, crc)

        if not is_valid:
            print("  Invalid packet!")
        print()


if __name__ == "__main__":
    main()

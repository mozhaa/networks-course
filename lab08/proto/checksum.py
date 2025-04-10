def calculate_checksum(data: bytes) -> int:
    total = 0
    for i in range(0, len(data), 2):
        if i + 1 < len(data):
            total += (data[i] << 8) + data[i + 1]
        else:
            total += data[i] << 8
    total = (total >> 16) + (total & 0xFFFF)
    total = ~total & 0xFFFF
    return total


def verify_checksum(data: bytes, received_checksum: int) -> bool:
    return calculate_checksum(data) == received_checksum


def run_tests() -> None:
    test_cases = [
        b"Hello, World!",
        b"Test data",
        b"",
        b"\x01\x02\x03\x04",
        b"\xff\xff\xff\xff",
        b"\x01\x02\x03\x04" * 10,
    ]

    results = []

    for data in test_cases:
        result = calculate_checksum(data)
        results.append(result)
        assert verify_checksum(data, result)
        assert not verify_checksum(data + b"\xaf", result)
        assert not verify_checksum(data[:-1] + b"\x10", result)
        assert not verify_checksum(b"\x10" + data[1:], result)

    # no repeats
    assert len(set(results)) == len(test_cases)

    print("Test success!")


if __name__ == "__main__":
    run_tests()

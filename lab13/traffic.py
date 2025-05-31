import time
from typing import Tuple

import psutil


def get_network_traffic() -> Tuple[int, int]:
    net_io = psutil.net_io_counters()
    return net_io.bytes_sent, net_io.bytes_recv


def main() -> None:
    initial_sent, initial_recv = get_network_traffic()

    while True:
        time.sleep(1)
        current_sent, current_recv = get_network_traffic()
        sent_diff = current_sent - initial_sent
        recv_diff = current_recv - initial_recv
        print(f"Outgoing: {sent_diff / 1024:.2f} KB/s | Incoming: {recv_diff / 1024:.2f} KB/s")
        initial_sent, initial_recv = current_sent, current_recv


if __name__ == "__main__":
    main()

import threading
import ipaddress
import socket
import os
from typing import List, Tuple


def ping_ip(ip: str) -> bool:
    process = os.system(f"ping -n 1 -w 1 {ip} >nul")
    return process == 0


def get_host_name(ip: str) -> str:
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return ""


def get_ips_by_net(net: str) -> List[str]:
    return list(map(str, ipaddress.ip_network(net, strict=False)))


def get_my_ip() -> str:
    return socket.gethostbyname(socket.gethostname())


def process_ip(ip: str, results: List[Tuple[str, str]]) -> None:
    if ping_ip(ip):
        hostname = get_host_name(ip)
        results.append((ip, hostname))


def main() -> None:
    my_ip = get_my_ip()
    mask = "255.255.255.0"
    ips = get_ips_by_net(my_ip + "/" + mask)

    print(f"Your IP: {my_ip} -- {get_host_name(my_ip)}")

    results = []
    threads = []

    for ip in ips:
        thread = threading.Thread(target=process_ip, args=(ip, results))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    results.sort(key=lambda x: x[0])
    for ip, hostname in results:
        print(f"{ip.ljust(15)} -- {hostname}")


if __name__ == "__main__":
    main()

import netifaces
import sys
from typing import List, Tuple


def get_ip_and_submask() -> List[Tuple[str, str]]:
    interfaces = netifaces.interfaces()
    results = []
    for interface in interfaces:
        addresses = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addresses:
            ip_info = addresses[netifaces.AF_INET][0]
            ip_address = ip_info["addr"]
            submask = ip_info["netmask"]
            results.append((ip_address, submask))
    return results


if __name__ == "__main__":
    results = get_ip_and_submask()
    if len(results) == 0:
        print("Failed to get IP Address and Subnet Mask.")
        sys.exit(1)
    else:
        for ip_address, submask in results:
            print(f"IP Address:\t{ip_address}")
            print(f"Subnet Mask:\t{submask}")
            print()

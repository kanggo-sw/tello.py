from socket import AF_INET

from netaddr import IPNetwork
from netifaces import interfaces, ifaddresses


def get_subnets():
    """
    Look through the server's internet connection and
    returns subnet addresses and server ip
    :return: list[str]: subnets
             list[str]: addr_list
    """
    subnets = []
    ifaces = interfaces()
    addr_list = []
    for myiface in ifaces:
        addrs = ifaddresses(myiface)
        if AF_INET not in addrs:
            continue
        # Get ipv4 stuff
        ipinfo = addrs[AF_INET][0]
        address = ipinfo["addr"]
        netmask = ipinfo["netmask"]
        # limit range of search. This will work for router subnets
        if netmask != "255.255.255.0":
            continue
        # Create ip object and get
        cidr = IPNetwork("%s/%s" % (address, netmask))
        network = cidr.network
        subnets.append((network, netmask))
        addr_list.append(address)
    return subnets, addr_list

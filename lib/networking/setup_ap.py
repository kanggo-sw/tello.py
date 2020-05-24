from socket import socket, AF_INET, SOCK_DGRAM

localhost: str = "192.168.10.1"
binding_port: int = 8889


def setup_ap(ssid: str, password: str):
    """
    Sets up tello
    :param ssid: the ssid of your network
    :param password: the password of your network
    :return:
    """

    if not (isinstance(ssid, str) and isinstance(password, str)):
        raise TypeError(
            "All arguments takes str. but got ({}, {})".format(
                type(ssid), type(password)
            )
        )

    tello_socket = socket(AF_INET, SOCK_DGRAM)
    tello_socket.bind(("", binding_port))

    address: tuple = (localhost, binding_port)

    tello_socket.sendto("command".encode("utf-8"), address)
    # if res.upper() != "OK":
    #     raise

    tello_socket.sendto(
        "ap {ssid} {password}".format(ssid=ssid, password=password).encode("utf-8"),
        address,
    )
    response, ip = tello_socket.recvfrom(100)

    if isinstance(response, bytes) and response.decode().upper() == "OK":
        print("Done.")
    else:
        raise ConnectionError("Response from {}: {}".format(ip, response))

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
            "All arguments take str. but got ({}, {})".format(
                type(ssid), type(password)
            )
        )

    tello_socket = socket(AF_INET, SOCK_DGRAM)
    tello_socket.bind(("", binding_port))

    address: tuple = (localhost, binding_port)

    tello_socket.sendto("command".encode("utf-8"), address)
    # if res.upper() != "OK":
    #     raise

    ap_str = "ap {ssid} {password}".format(ssid=ssid, password=password)
    print("Send '{}'...".format(ap_str, address), end="")
    tello_socket.sendto(
        ap_str.encode("utf-8"),
        address,
    )
    response, ip = tello_socket.recvfrom(100)

    try:
        if isinstance(response, bytes) and response.decode().upper() == "OK":
            print("OK.")
        else:
            print("Connection lost.")
            raise ConnectionError("Response from {}: {}".format(ip, response))

    except UnicodeDecodeError:
        print("There was a problem while decoding response data.")
        print("{}:".format(ip), response)

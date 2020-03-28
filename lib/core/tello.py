from lib._kernel import TelloKernel


class Tello(object):
    """
    A wrapper class to interact with Tello
    """

    def __init__(self, tello_ip, kernel: TelloKernel):
        self._tello_ip = tello_ip
        self._kernel = kernel

    def send_command(self, command):
        return self._kernel.send_command(command, self._tello_ip)

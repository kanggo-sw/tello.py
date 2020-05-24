from lib.tello.swarm import TelloKernel


class Tello(object):
    """
    A wrapper class to interact with Tello
    """

    def __init__(self, tello_ip, kernel: TelloKernel):
        self.tello_ip = tello_ip
        self._kernel = kernel

    def send_command(self, command: str):
        return self._kernel.send_command(str(command), self.tello_ip)

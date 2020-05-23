from lib.compat.v3 import Tello

tello = Tello("", 8889, imperial=False, command_timeout=1, tello_ip="127.0.0.1")

tello.takeoff()

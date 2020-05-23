# A basic Tello simulator for testing UDP commands
# This script is part of our course on Tello drone programming
# https://learn.droneblocks.io/p/tello-drone-programming-with-python/


import socket
import threading
import time

# Address of this computer and port simulating Tello
tello_address = ('127.0.0.1', 8889)

# Create a local socket and bind to it
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(tello_address)

# Tello's address
tello_commands = ["command", "takeoff", "land", "forward", "back", "up", "down", "left", "right", "go", "curve", "cw",
                  "ccw", "flip", "speed", "Speed?", "Battery?", "Time?"]


def recv():
    print("recv...")
    while True:
        try:
            data, address = sock.recvfrom(2048)
            print("Received command: " + data.decode(encoding="utf-8") + " from: {0}".format(address))
            reply = response(data.decode(encoding="utf-8"))
            # Delay before we respond back
            time.sleep(1)
            sock.sendto(reply, address)
        except Exception as e:
            print('\nExit . . .\n' + str(e))
            break


def response(data):
    data: str = data.split()

    if data[0] == "battery?":
        return b"75"
    elif data[0] in tello_commands:
        return b"OK"
    else:
        return b"Unknown command" + data[0].encode(encoding="utf8") + b" "


# def send():
#  battery = 100
#  while True:
#    try:
#      print("sending")
#      sock.sendto(str(battery).encode(), tello_address)
#      time.sleep(10)
#      battery = battery - 1
#    except Exception as e:
#      print (str(e))
#      break


recvThread = threading.Thread(target=recv)
recvThread.daemon = True
recvThread.start()

# So we can kill the script with ctrl-c
while True:
    time.sleep(1)

# sendThread = threading.Thread(target=send)
# sendThread.start()

from lib.tello.swarm import Tello

tello_serials: list = ["0TQDG8EEDB51PF", "0TQDG8PEDBMP41"]

tello = Tello(tello_serials)

tello.takeoff()

tello.up(10, 1)
tello.down(10, 2)

tello.up(10, 2)
tello.down(10, 1)

tello.wait_sync()

tello.land()

print("Done.")

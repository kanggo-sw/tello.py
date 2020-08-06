from lib.tello.swarm import Tello  # Import Tello

my_tellos = list()
my_tellos.append('')  # Replace with your Tello Serial Number

with Tello(my_tellos) as tello:
    tello.takeoff()  # 이륙합니다.
    tello.forward(50)  # 앞쪽 방향으로 50cm 이동합니다. 이 숫자의 최솟값은 25, 최댓값은 500 입니다.

    with tello.sync_these():  # 군집비행 시, 명령을 동기화합니다.
        tello.left(50, tello=1)  # 1번 텔로만 뒤쪽으로 50cm 이동합니다. 이 숫자의 최솟값은 25, 최댓값은 500 입니다.

    tello.flip(direction='forward')  # 앞쪽 방향으로 flip 합니다.
    tello.land()  # 착륙합니다.

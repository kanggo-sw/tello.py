# https://github.com/Virodroid/easyTello

import socket
import threading
import time
from datetime import datetime

import cv2


class Stats:
    def __init__(self, command: str, _id: int):
        self.command = command
        self.response = None
        self.id = _id

        self.start_time = datetime.now()
        self.end_time = None
        self.duration = None

    def add_response(self, response: str):
        self.response = str(response)
        # Calculating total time taken to execute command
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()

    def got_response(self):
        if self.response is None:
            return False
        else:
            return True

    def get_raw_response(self):
        return self.response

    @staticmethod
    def numeric_response(data: str):
        num_val = ''.join(i for i in data if i.isdigit() or i == '-' or i == '.')
        return num_val

    def int_response(self, data: str):
        return int(self.numeric_response(data))

    def float_response(self, data: str):
        return float(self.numeric_response(data))

    def attitude_response(self):
        raw_att = self.response.split(';')
        att_data = (self.int_response(raw_att[0]), self.int_response(raw_att[1]), self.int_response(raw_att[2]))
        return att_data

    def acceleration_response(self):
        raw_acc = self.response.split(';')
        acc_data = (self.float_response(raw_acc[0]), self.float_response(raw_acc[1]), self.float_response(raw_acc[2]))
        return acc_data

    def temp_response(self):
        raw_temp = self.response.split('~')
        temp = (self.int_response(raw_temp[0]) + self.int_response(raw_temp[1])) / 2
        return temp

    def get_response(self):
        if 'attitude?' in self.command:
            return self.attitude_response()
        elif 'acceleration?' in self.command:
            return self.acceleration_response()
        elif 'temp?' in self.command:
            return self.temp_response()
        elif 'baro?' in self.command or 'speed?' in self.command:
            return self.float_response(self.response)
        elif '?' not in self.command:
            return self.get_raw_response()
        else:
            return self.int_response(self.response)


class Tello(object):
    def __init__(self, tello_ip: str = '192.168.10.1', debug: bool = True):
        # Opening local UDP port on 8889 for Tello communication
        self.local_ip = ''
        self.local_port = 8889
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.local_ip, self.local_port))

        # Setting Tello ip and port info
        self.tello_ip = tello_ip
        self.tello_port = 8889
        self.tello_address = (self.tello_ip, self.tello_port)
        self.log = []

        # Intializing response thread
        self.receive_thread = threading.Thread(target=self._receive_thread)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        # easyTello runtime options
        self.stream_state = False
        self.MAX_TIME_OUT = 15.0
        self.debug = debug

        self.video_thread = None
        # Setting Tello to command mode
        self.command()

    def send_command(self, command: str, query: bool = False):
        # New log entry created for the outbound command
        self.log.append(Stats(command, len(self.log)))

        # Sending command to Tello
        self.socket.sendto(command.encode('utf-8'), self.tello_address)
        # Displaying conformation message (if 'debug' os True)
        if self.debug is True:
            print('Sending command: {}'.format(command))

        # Checking whether the command has timed out or not (based on value in 'MAX_TIME_OUT')
        start = time.time()
        while not self.log[-1].got_response():  # Runs while no repsonse has been received in log
            now = time.time()
            difference = now - start
            if difference > self.MAX_TIME_OUT:
                print('Connection timed out!')
                break
        # Prints out Tello response (if 'debug' is True)
        if self.debug is True and query is False:
            print('Response: {}'.format(self.log[-1].get_response()))

    def _receive_thread(self):
        while True:
            # Checking for Tello response, throws socket error
            try:
                self.response, ip = self.socket.recvfrom(1024)
                self.log[-1].add_response(self.response)
            except socket.error as exc:
                print('Socket error: {}'.format(exc))

    def _video_thread(self):
        # Creating stream capture object
        cap = cv2.VideoCapture('udp://' + self.tello_ip + ':11111')
        # Runs while 'stream_state' is True
        while self.stream_state:
            ret, frame = cap.read()
            cv2.imshow('DJI Tello', frame)

            # Video Stream is closed if escape key is pressed
            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                break
        cap.release()
        cv2.destroyAllWindows()

    def wait(self, delay: float):
        # Displaying wait message (if 'debug' is True)
        if self.debug is True:
            print('Waiting {} seconds...'.format(delay))
        # Log entry for delay added
        self.log.append(Stats('wait', len(self.log)))
        # Delay is activated
        time.sleep(delay)

    def get_log(self):
        return self.log

    # Controll Commands
    def command(self):
        self.send_command('command')

    def takeoff(self):
        self.send_command('takeoff')

    def land(self):
        self.send_command('land')

    def streamon(self):
        self.send_command('streamon')
        self.stream_state = True
        self.video_thread = threading.Thread(target=self._video_thread)
        self.video_thread.daemon = True
        self.video_thread.start()

    def streamoff(self):
        self.stream_state = False
        self.send_command('streamoff')

    def emergency(self):
        self.send_command('emergency')

    # Movement Commands
    def up(self, dist: int):
        self.send_command('up {}'.format(dist))

    def down(self, dist: int):
        self.send_command('down {}'.format(dist))

    def left(self, dist: int):
        self.send_command('left {}'.format(dist))

    def right(self, dist: int):
        self.send_command('right {}'.format(dist))

    def forward(self, dist: int):
        self.send_command('forward {}'.format(dist))

    def back(self, dist: int):
        self.send_command('back {}'.format(dist))

    def cw(self, degr: int):
        self.send_command('cw {}'.format(degr))

    def ccw(self, degr: int):
        self.send_command('ccw {}'.format(degr))

    def flip(self, direc: str):
        self.send_command('flip {}'.format(direc))

    def go(self, x: int, y: int, z: int, speed: int):
        self.send_command('go {} {} {} {}'.format(x, y, z, speed))

    def curve(self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, speed: int):
        self.send_command('curve {} {} {} {} {} {} {}'.format(x1, y1, z1, x2, y2, z2, speed))

    # Set Commands
    def set_speed(self, speed: int):
        self.send_command('speed {}'.format(speed))

    def rc_control(self, a: int, b: int, c: int, d: int):
        self.send_command('rc {} {} {} {}'.format(a, b, c, d))

    def set_wifi(self, ssid: str, passwrd: str):
        self.send_command('wifi {} {}'.format(ssid, passwrd))

    # Read Commands
    def get_speed(self):
        self.send_command('speed?', True)
        return self.log[-1].get_response()

    def get_battery(self):
        self.send_command('battery?', True)
        return self.log[-1].get_response()

    def get_time(self):
        self.send_command('time?', True)
        return self.log[-1].get_response()

    def get_height(self):
        self.send_command('height?', True)
        return self.log[-1].get_response()

    def get_temp(self):
        self.send_command('temp?', True)
        return self.log[-1].get_response()

    def get_attitude(self):
        self.send_command('attitude?', True)
        return self.log[-1].get_response()

    def get_baro(self):
        self.send_command('baro?', True)
        return self.log[-1].get_response()

    def get_acceleration(self):
        self.send_command('acceleration?', True)
        return self.log[-1].get_response()

    def get_tof(self):
        self.send_command('tof?', True)
        return self.log[-1].get_response()

    def get_wifi(self):
        self.send_command('wifi?', True)
        return self.log[-1].get_response()

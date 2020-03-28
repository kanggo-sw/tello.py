from collections import defaultdict
from socket import socket, AF_INET, SOCK_DGRAM, error
from threading import Thread
from time import time, sleep
from typing import Union, List

from netaddr import IPNetwork
from netifaces import interfaces, ifaddresses

from lib.core.tello import Tello
from lib.core.tello_stats import TelloStats


class TelloKernel(object):
    # TODO: Use logging, not a print

    def __init__(
        self, local_ip: str = "", local_port: int = 8889, timeout: Union[int, float] = 3
    ):
        self.local_ip: str = local_ip
        self.local_port: int = local_port

        self.socket: socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind((self.local_ip, self.local_port))

        self.receive_thread: Thread = Thread(target=self._receive_thread)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        self.tello_ip_list: list = []
        self.tello_list: list = []
        self.log = defaultdict(list)
        self.response: Union[bytes, List[bytes], None] = None
        self.COMMAND_TIME_OUT = float(timeout)
        self.last_response_index: dict = {}
        self.str_cmd_index: dict = {}

    def find_avaliable_tello(self, num):
        """
        Find avaliable tello in server's subnets
        :param num: Number of Tello this method is expected to find
        :return: None
        """
        print("[+]Searching for {} available Tello...\n".format(num))
        subnets, address = self.get_subnets()
        possible_addr = []
        for subnet, netmask in subnets:
            for ip in IPNetwork("%s/%s" % (subnet, netmask)):
                # skip local and broadcast
                if str(ip).split(".")[3] == "0" or str(ip).split(".")[3] == "255":
                    continue
                possible_addr.append(str(ip))
        while len(self.tello_ip_list) < num:
            print("[!]Trying to find Tello in subnets...\n")
            # delete already found Tello
            for tello_ip in self.tello_ip_list:
                if tello_ip in possible_addr:
                    possible_addr.remove(tello_ip)
            # skip server itself
            for ip in possible_addr:
                if ip in address:
                    continue
                # record this command
                self.log[ip].append(TelloStats("command", len(self.log[ip])))
                self.socket.sendto("command".encode("utf-8"), (ip, self.local_port))
            sleep(5)
        # filter out non-tello addresses in log
        temp = defaultdict(list)
        for ip in self.tello_ip_list:
            temp[ip] = self.log[ip]
        self.log = temp

    @staticmethod
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

    def get_tello_list(self):
        return self.tello_list

    def send_command(self, command: str, ip: str):
        """
        Send a command to the ip address. Will be blocked until
        the last command receives an 'OK'.
        If the command fails (either b/c time out or error),
        will try to resend the command
        :param command: (str) the command to send
        :param ip: (str) the ip of Tello
        :return: The latest command response
        """
        # global cmd
        command_sof_1 = ord(command[0])
        command_sof_2 = ord(command[1])
        if command_sof_1 == 0x52 and command_sof_2 == 0x65:
            multi_cmd_send_flag = True
        else:
            multi_cmd_send_flag = False
        if multi_cmd_send_flag:
            self.str_cmd_index[ip] = self.str_cmd_index[ip] + 1
            for num in range(1, 5):
                str_cmd_index_h = self.str_cmd_index[ip] / 128 + 1
                str_cmd_index_l = self.str_cmd_index[ip] % 128
                if str_cmd_index_l == 0:
                    str_cmd_index_l = str_cmd_index_l + 2
                cmd_sof = [
                    0x52,
                    0x65,
                    str_cmd_index_h,
                    str_cmd_index_l,
                    0x01,
                    num + 1,
                    0x20,
                ]
                cmd_sof_str = str(bytearray(cmd_sof))
                cmd = cmd_sof_str + command[3:]
                self.socket.sendto(cmd.encode("utf-8"), (ip, self.local_port))
            print(
                "[Multi_Command]----Multi_Send----IP:{}----Command:   {}\n".format(
                    ip, command[3:]
                )
            )
            real_command = command[3:]
        else:
            self.socket.sendto(command.encode("utf-8"), (ip, self.local_port))
            print(
                "[Single_Command]----Single_Send----IP:{}----Command:   {}\n".format(
                    ip, command
                )
            )
            real_command = command
        self.log[ip].append(TelloStats(real_command, len(self.log[ip])))
        start = time()
        while not self.log[ip][-1].got_response():
            now = time()
            diff = now - start
            if diff > self.COMMAND_TIME_OUT:
                print("[-]Max timeout exceeded...command: {} \n".format(real_command))
                return

    def _receive_thread(self):
        while True:
            try:
                self.response, ip = self.socket.recvfrom(1024)
                self.response: Union[bytes, List[bytes], None]
                ip = "".join(str(ip[0]))
                if (
                    ip not in self.tello_ip_list
                    and hasattr(self.response, "upper")
                    and self.response.upper() == "OK"
                ):
                    print("[+]Found Tello.The Tello ip is:{}\n".format(ip))
                    self.tello_ip_list.append(ip)
                    self.last_response_index[ip] = 100
                    self.tello_list.append(Tello(ip, self))
                    self.str_cmd_index[ip] = 1
                response_sof_part1 = ord(self.response[0])
                response_sof_part2 = ord(self.response[1])
                if response_sof_part1 == 0x52 and response_sof_part2 == 0x65:
                    response_index = ord(self.response[3])
                    if response_index != self.last_response_index[ip]:
                        print(
                            "[Multi_Response] ----Multi_Receive----IP:%s----Response:   %s ----\n"
                            % (ip, self.response[7:])
                        )
                        self.log[ip][-1].add_response(self.response[7:], ip)
                    self.last_response_index[ip] = response_index
                else:
                    print(
                        "[Single_Response]----Single_Receive----IP:%s----Response:   %s ----\n"
                        % (ip, self.response)
                    )
                    self.log[ip][-1].add_response(self.response, ip)
            except error as err:
                print("error caught!\n{}".format(err))

    def get_log(self):
        return self.log
# TODO: This is an temporary module for compatibility and need to rewrite.

import os
import queue
from threading import Thread
from time import sleep, time, strftime, localtime

from lib._kernel import TelloKernel

start_time = str(strftime("%a-%d-%b-%Y_%H-%M-%S-%Z", localtime(time())))


def create_execution_pools(num):
    pools = []
    for _ in range(num):
        execution_pool = queue.Queue()
        pools.append(execution_pool)
    return pools


def drone_handler(tello, _queue):
    while True:
        while _queue.empty():
            pass
        _command = _queue.get()
        tello.send_command(_command)


def all_queue_empty(_execution_pools):
    for _queue in _execution_pools:
        if not _queue.empty():
            return False
    return True


def all_got_response(_kernel):
    for _tello_log in list(_kernel.get_log().values()):
        if not _tello_log[-1].got_response():
            return False
    return True


def save_log(_kernel):
    '''log = _kernel.get_log()
    if not os.path.exists("log"):
        os.makedirs("log")
    out = open("log/" + start_time + ".txt", "w")
    cnt = 1
    for stat_list in list(log.values()):
        out.write("------\nDrone: %s\n" % cnt)
        cnt += 1
        for stat in stat_list:
            # stat.print_stats()
            _stat = stat.return_stats()
            out.write(_stat)
        out.write("\n")'''


def check_timeout(_start_time, _end_time, _timeout):
    _diff = _end_time - _start_time
    sleep(0.1)
    return _diff > _timeout


class ControllerTest(object):
    @staticmethod
    def original(file: str):
        tello_kernel = TelloKernel()
        try:
            file_name = file
            f = open(file_name)
            commands = f.readlines()
            tello_list = []
            execution_pools = []
            sn_ip_dict = {}
            id_sn_dict = {}
            ip_fid_dict = {}

            for command in commands:
                if command != "" and command != "\n":
                    command = command.rstrip()
                    if "//" in command:
                        # ignore comments
                        continue
                    elif "scan" in command:
                        num_of_tello = int(command.partition("scan")[2])
                        tello_kernel.find_avaliable_tello(num_of_tello)
                        tello_list = tello_kernel.get_tello_list()
                        execution_pools = create_execution_pools(num_of_tello)
                        for x in range(len(tello_list)):
                            t1 = Thread(
                                target=drone_handler,
                                args=(tello_list[x], execution_pools[x]),
                            )
                            ip_fid_dict[tello_list[x].tello_ip] = x
                            # str_cmd_index_dict_init_flag [x] = None
                            t1.daemon = True
                            t1.start()
                    elif ">" in command:
                        id_list = []
                        _id = command.partition(">")[0]
                        if _id == "*":
                            for x in range(len(tello_list)):
                                id_list.append(x)
                        else:
                            # index starbattery_checkt from 1
                            id_list.append(int(_id) - 1)
                        action = str(command.partition(">")[2])
                        print(_id, action)
                        # push command to pools
                        for tello_id in id_list:
                            tmp_sn = id_sn_dict[tello_id]
                            reflec_ip = sn_ip_dict[tmp_sn]
                            fid = ip_fid_dict[reflec_ip]
                            execution_pools[fid].put(action)
                    elif "battery_check" in command:
                        threshold = int(command.partition("battery_check")[2])
                        for _queue in execution_pools:
                            _queue.put("battery?")
                        # wait till all commands are executed
                        while not all_queue_empty(execution_pools):
                            sleep(0.5)
                        # wait for new log object append
                        sleep(1)
                        # wait till all responses are received
                        while not all_got_response(tello_kernel):
                            sleep(0.5)
                        for tello_log in list(tello_kernel.get_log().values()):
                            battery = int(tello_log[-1].response)
                            print(
                                (
                                    "[Battery_Show]show drone battery: %d  ip:%s\n"
                                    % (battery, tello_log[-1].drone_ip)
                                )
                            )
                            if battery < threshold:
                                print(
                                    (
                                        "[Battery_Low]IP:%s  Battery < Threshold. Exiting...\n"
                                        % tello_log[-1].drone_ip
                                    )
                                )
                                save_log(tello_kernel)
                                exit(0)
                        print("[Battery_Enough]Pass battery check\n")
                    elif "delay" in command:
                        delay_time = float(command.partition("delay")[2])
                        print(
                            ("[Delay_Seconds]Start Delay for %f second\n" % delay_time)
                        )
                        sleep(delay_time)
                    elif "correct_ip" in command:
                        for _queue in execution_pools:
                            _queue.put("sn?")
                        while not all_queue_empty(execution_pools):
                            sleep(0.5)
                        sleep(1)
                        while not all_got_response(tello_kernel):
                            sleep(0.5)
                        for tello_log in list(tello_kernel.get_log().values()):
                            sn = str(tello_log[-1].response)
                            tello_ip = str(tello_log[-1].drone_ip)
                            sn_ip_dict[sn] = tello_ip
                    elif "=" in command:
                        drone_id = int(command.partition("=")[0])
                        drone_sn = command.partition("=")[2]
                        id_sn_dict[drone_id - 1] = drone_sn
                        print(
                            (
                                "[IP_SN_FID]:Tello_IP:%s------Tello_SN:%s------Tello_fid:%d\n"
                                % (sn_ip_dict[drone_sn], drone_sn, drone_id)
                            )
                        )
                        # print id_sn_dict[drone_id]
                    elif "sync" in command:
                        timeout = float(command.partition("sync")[2])
                        print("[Sync_And_Waiting]Sync for %s seconds \n" % timeout)
                        sleep(1)
                        try:
                            start = time()
                            # wait till all commands are executed
                            while not all_queue_empty(execution_pools):
                                now = time()
                                if check_timeout(start, now, timeout):
                                    raise RuntimeError
                            print(
                                "[All_Commands_Send]All queue empty and all command send,continue\n"
                            )
                            # wait till all responses are received
                            while not all_got_response(tello_kernel):
                                now = time()
                                if check_timeout(start, now, timeout):
                                    raise RuntimeError
                            print("[All_Responses_Get]All response got, continue\n")
                        except RuntimeError:
                            print(
                                "[Quit_Sync]Fail Sync:Timeout exceeded, continue...\n"
                            )

            # wait till all commands are executed
            while not all_queue_empty(execution_pools):
                sleep(0.5)
            sleep(1)
            # wait till all responses are received
            while not all_got_response(tello_kernel):
                sleep(0.5)
            save_log(tello_kernel)
        except KeyboardInterrupt:
            print("[Quit_ALL]Exit requested. Sending land to all drones...\n")
            for ip in tello_kernel.tello_ip_list:
                tello_kernel.socket.sendto("land".encode("utf-8"), (ip, 8889))
        except Exception as e:
            print(e)
            print(
                "[Quit_ALL]Multi_Tello_Task got exception. Sending land to all drones...\n"
            )
            for ip in tello_kernel.tello_ip_list:
                tello_kernel.socket.sendto("land".encode("utf-8"), (ip, 8889))
            save_log(tello_kernel)

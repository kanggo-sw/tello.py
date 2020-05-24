import os
import time
from datetime import date
from queue import Queue
from threading import Thread
from typing import List, Dict, Iterable

from compiler.parser import Token
from lib.tello.swarm import TelloKernel
from lib.core.tello_device import Tello

start_time: str = date.today().isoformat()


def create_execution_pools(num: int) -> List[Queue]:
    pools: List[Queue] = []
    for _ in range(num):
        pools.append(Queue())
    return pools


def _drone_handler_thread(tello: Tello, _queue: Queue):
    while True:
        while _queue.empty():
            pass
        tello.send_command(_queue.get())


def is_all_queue_empty(_execution_pools: List[Queue]) -> bool:
    for _queue in _execution_pools:
        if not _queue.empty():
            return False
    return True


def did_all_get_response(_kernel: TelloKernel) -> bool:
    for _tello_log in list(_kernel.get_log().values()):
        if not _tello_log[-1].got_response():
            return False
    return True


def save_log(_kernel: TelloKernel):
    log = _kernel.get_log()
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
        out.write("\n")


def check_timeout(_start_time, _end_time, _timeout) -> bool:
    return (_end_time - _start_time) > _timeout


tello_kernel: TelloKernel = TelloKernel()


def execute(source: Iterable[Token]) -> bool:
    tello_list: List[Tello] = []
    execution_pools: List[Queue[str]] = []

    sn_ip_dict: Dict[str, str] = dict()
    id_sn_dict: Dict = dict()
    ip_fid_dict: Dict = dict()

    for token in source:
        if not token.command:
            continue

        if token.target is not None:
            if token.command == "=":
                if token.target == "*":
                    raise SyntaxError
                drone_id: int = int(token.target)
                drone_sn: str = token.args
                id_sn_dict[drone_id - 1] = drone_sn
                print(
                    (
                        "[IP_SN_FID]:Tello_IP:%s------Tello_SN:%s------Tello_fid:%d\n"
                        % (sn_ip_dict[drone_sn], drone_sn, drone_id)
                    )
                )
            else:
                _id_list: List[int] = []
                if token.target == "*":
                    for x in range(len(tello_list)):
                        _id_list.append(x)
                else:
                    _id_list.append(int(token.target) - 1)

                for _id in _id_list:
                    if token.args is not None:
                        execution_pools[ip_fid_dict[sn_ip_dict[id_sn_dict[_id]]]].put(
                            "{} {}".format(token.command, token.args)
                        )
                    else:
                        execution_pools[ip_fid_dict[sn_ip_dict[id_sn_dict[_id]]]].put(
                            token.command,
                        )

        else:
            if token.command == "sync":
                timeout = float(token.args)
                print("[Sync_And_Waiting]Sync for %s seconds \n" % timeout)
                time.sleep(1)
                try:
                    start = time.time()
                    # wait till all commands are executed
                    while not is_all_queue_empty(execution_pools):
                        now = time.time()
                        if check_timeout(start, now, timeout):
                            raise RuntimeError
                    print(
                        "[All_Commands_Send]All queue empty and all command send,continue\n"
                    )
                    # wait till all responses are received
                    while not did_all_get_response(tello_kernel):
                        now = time.time()
                        if check_timeout(start, now, timeout):
                            raise RuntimeError
                    print("[All_Responses_Get]All response got, continue\n")
                except RuntimeError:
                    print("[Quit_Sync]Fail Sync:Timeout exceeded, continue...\n")

            elif token.command == "scan":
                _num_of_tello = int(token.args)
                tello_kernel.find_available_tello(_num_of_tello)
                tello_list = tello_kernel.get_tello_list()
                execution_pools: List[Queue[str]] = create_execution_pools(
                    _num_of_tello
                )
                for x in range(len(tello_list)):
                    ip_fid_dict[tello_list[x].tello_ip] = x
                    t1 = Thread(
                        target=_drone_handler_thread,
                        args=(tello_list[x], execution_pools[x]),
                    )
                    t1.daemon = True
                    t1.start()

            elif token.command == "battery_check":
                threshold = int(token.args)
                for _queue in execution_pools:
                    _queue.put("battery?")
                while not is_all_queue_empty(execution_pools):
                    time.sleep(0.5)
                # wait for new log object append
                time.sleep(1)
                while not did_all_get_response(tello_kernel):
                    time.sleep(0.5)
                for tello_log in list(tello_kernel.get_log().values()):
                    battery: int = int(tello_log[-1].response)
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

            elif token.command == "delay":
                delay_time = float(token.args)
                print(("[Delay_Seconds]Start Delay for %f second\n" % delay_time))
                time.sleep(delay_time)

            elif token.command == "correct_ip":
                for _queue in execution_pools:
                    _queue.put("sn?")
                while not is_all_queue_empty(execution_pools):
                    time.sleep(0.5)
                time.sleep(1)
                while not did_all_get_response(tello_kernel):
                    time.sleep(0.5)
                for tello_log in list(tello_kernel.get_log().values()):
                    sn: str = tello_log[-1].response.decode()
                    tello_ip = str(tello_log[-1].drone_ip)
                    sn_ip_dict[sn] = tello_ip

            else:
                raise NotImplementedError(
                    "Command {} is not implemented.".format(token.command)
                )

    return True

import os
from datetime import date
from queue import Queue
from typing import List, Dict, Iterable

from compiler.parser import Token
from lib._kernel import TelloKernel
from lib.core.tello import Tello

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


def execute(source: Iterable[Token]) -> bool:
    tello_list: List[Tello] = []
    execution_pools: List[Queue] = []

    sn_ip_dict: Dict = dict()
    id_sn_dict: Dict = dict()
    ip_fid_dict: Dict = dict()

    for token in source:
        if not token.command:
            continue

        print(token.command)

    return True

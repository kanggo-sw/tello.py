import logging
import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from pprint import pprint

import compiler
from lib.networking.controller_v2 import execute, tello_kernel

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s][%(levelname)s] in function %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)

if __name__ == "__main__":
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

    run_subparser = parser.add_subparsers(help="Tello script interpreter")
    run_parser = run_subparser.add_parser("run")

    run_parser.add_argument("code", help="Source code file", type=str, nargs="?")

    args = parser.parse_args()

    if hasattr(args, "code") and args.code:
        code = compiler.main(args.code)
        ...

        pprint(code)

        try:
            execute(source=code)
        except NotImplementedError:
            raise
        except RuntimeError:
            raise
        except Exception as e:
            print(e)
            print("Landing all drones...")
            for ip in tello_kernel.tello_ip_list:
                tello_kernel.socket.sendto("land".encode("utf-8"), (ip, 8889))
            print("Done.")

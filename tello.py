import logging
import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

import compiler
from lib.networking import controller

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s][%(levelname)s] in %(funcName)s(): %(message)s",
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

        controller.ControllerTest.original(args.code)

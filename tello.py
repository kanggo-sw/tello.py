import logging
import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

import compiler

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s][%(levelname)s] in %(funcName)s(): %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)

if __name__ == '__main__':
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument("code", help="Source code file", type=str, nargs="?")

    args = parser.parse_args()

    if hasattr(args, "code") and args.code:
        compiler.main(args.code)

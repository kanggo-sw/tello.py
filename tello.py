import logging
import sys
from argparse import ArgumentParser

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s][%(levelname)s] in function %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)

if __name__ == "__main__":
    parser = ArgumentParser(
        # formatter_class=ArgumentDefaultsHelpFormatter
    )

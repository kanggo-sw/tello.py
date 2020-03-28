from typing import Tuple

version_tuple: Tuple[int, int, int] = (2020, 3, 8)

version: str = "Tello.py {version}".format(
    version=".".join(str(x) for x in version_tuple)
)

description: str = "Next-generation programming language for tello-edu"

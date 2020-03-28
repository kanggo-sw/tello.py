from typing import Tuple, List

import compiler


def main(file: str) -> List[dict]:
    program_loader = compiler.Loader.from_file(file)

    token: list = []

    for command in program_loader.query():

        token.append(command)

    return token

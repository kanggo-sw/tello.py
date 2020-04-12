from typing import List

import compiler
from compiler.parser import Token, parse


def main(file: str) -> List[Token]:
    program_loader = compiler.Loader.from_file(file)

    tokens_iter: List[Token] = []

    for string in program_loader.query():
        if not string:
            continue
        token: Token = parse(string.strip())

        tokens_iter.append(token)

    return tokens_iter

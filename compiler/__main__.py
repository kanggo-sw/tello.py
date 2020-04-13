from typing import List

import compiler
from compiler.parser import Token, parse


def main(file: str) -> List[Token]:
    program_loader = compiler.Loader.from_file(file)

    tokens_iter: List[Token] = []

    for line, string in enumerate(program_loader.query()):
        if not string:
            continue

        token: Token = parse(string.strip())

        if token is NotImplemented:
            raise NotImplementedError("{} (Line {})".format(string, line))

        tokens_iter.append(token)

    return tokens_iter

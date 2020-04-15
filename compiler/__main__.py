from typing import List

import compiler
from compiler.parser import Token, parse_string


def main(file: str) -> List[Token]:
    program_loader = compiler.Loader.from_file(file)

    tokens_iter: List[Token] = []

    for line, string in enumerate(program_loader.query()):
        if not string or string.startswith("//"):
            continue

        token: Token = parse_string(string.strip())

        if token is NotImplemented:
            raise NotImplementedError(
                "{} (Line {})\n{}".format(
                    string, line + 1, " " * 21 + "^" * len(string)
                )
            )

        tokens_iter.append(token)

        # TODO: Semantic analyzer

    return tokens_iter

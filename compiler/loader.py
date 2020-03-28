from typing import List


class Loader(object):
    def __init__(self, lines: List[str]):
        self._lines: List[str] = [line.strip() for line in lines]

    def query(self) -> str:
        yield from self._lines

    @classmethod
    def from_file(cls, file: str):
        return cls(lines=open(file, encoding="utf-8").readlines())

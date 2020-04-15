from dataclasses import dataclass
from re import search
from typing import Union


@dataclass
class Token(object):
    target: Union[str, None]
    command: str
    args: Union[str, None]


def parse_string(raw_code: str) -> Token:
    _token: Token
    if ">" in raw_code:
        tokens = search(
            r"(?P<target>(\d+)?(\*)?) *> *(?P<command>[a-zA-Z]+) *(?P<args>.+)?",
            raw_code,
        )
        _token = Token(
            tokens.group("target"), tokens.group("command"), tokens.group("args")
        )
    elif raw_code == "correct_ip":
        _token = Token(None, raw_code, None)
    elif raw_code[:4] in ("scan", "sync"):
        tokens = search(r"(?P<c>\w{4}) *(?P<n>[0-9]+)", raw_code)
        _token = Token(None, tokens.group("c"), tokens.group("n"))
    elif raw_code[:5] == "delay":
        tokens = search(r"delay *(?P<n>[0-9]+)", raw_code)
        _token = Token(None, "delay", tokens.group("n"))
    elif raw_code[:13] == "battery_check":
        tokens = search(r"battery_check *(?P<n>[0-9]+)", raw_code)
        _token = Token(None, "battery_check", tokens.group("n"))
    elif "=" in raw_code:
        tokens = search(r"(?P<id>[0-9]+) *= *(?P<sn>[0-9a-zA-Z]+)", raw_code)
        _token = Token(tokens.group("id"), "=", tokens.group("sn"))
    else:
        return NotImplemented

    return _token

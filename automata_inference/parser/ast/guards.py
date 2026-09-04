from dataclasses import dataclass


class Guard:
    """Base class for guards."""


@dataclass(frozen=True)
class LessThan(Guard):
    variable: str
    value: int


@dataclass(frozen=True)
class ModuloEquals(Guard):
    variable: str
    modulus: int
    residue: int


@dataclass(frozen=True)
class Equals(Guard):
    variable: str
    value: int


@dataclass(frozen=True)
class Not(Guard):
    guard: Guard


@dataclass(frozen=True)
class And(Guard):
    left: Guard
    right: Guard


@dataclass(frozen=True)
class Or(Guard):
    left: Guard
    right: Guard


@dataclass(frozen=True)
class Implies(Guard):
    left: Guard
    right: Guard

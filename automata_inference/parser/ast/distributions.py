from symengine import Rational

from dataclasses import dataclass


class Distribution:
    """Base class..."""


@dataclass(frozen=True)
class Bernoulli(Distribution):
    p: Rational


@dataclass(frozen=True)
class Dirac(Distribution):
    n: int


@dataclass(frozen=True)
class Geometric(Distribution):
    p: Rational


@dataclass(frozen=True)
class Uniform(Distribution):
    n: int


@dataclass(frozen=True)
class NegBinom(Distribution):
    n: int
    p: Rational

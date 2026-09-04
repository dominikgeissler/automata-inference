from dataclasses import dataclass

from symengine import Rational


class Distribution:
    """Base class for parsed distributions."""


@dataclass(frozen=True)
class Bernoulli(Distribution):
    """Represents a Bernoulli distribution.
    
    Args:
        p (Rational): The probability of success for the Bernoulli distribution.
    """
    p: Rational


@dataclass(frozen=True)
class Dirac(Distribution):
    """Represents a Dirac distribution.

    Args:
        n (int): The value at which the Dirac distribution is concentrated.
    """
    n: int


@dataclass(frozen=True)
class Geometric(Distribution):
    """Represents a Geometric distribution.
    
    Args:
        p (Rational): The probability of success for the Geometric distribution.
    """
    p: Rational


@dataclass(frozen=True)
class Uniform(Distribution):
    """Represents a Uniform distribution.
    
    Args:
        n (int): The number of equally likely outcomes for the Uniform distribution.
    """
    n: int


@dataclass(frozen=True)
class NegBinom(Distribution):
    """Represents a negative binomial distribution.

    Args:
        n (int): The number of successes required for the negative binomial distribution.
        p (Rational): The probability of success for the negative binomial distribution.
    """
    n: int
    p: Rational

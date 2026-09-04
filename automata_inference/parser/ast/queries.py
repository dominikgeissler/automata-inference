from dataclasses import dataclass

from automata_inference.parser.ast.guards import Guard


class Query:
    """Base class for parsed queries."""


@dataclass(frozen=True)
class PosteriorProbability(Query):
    """Queries the PGA to obtain a satisfaction probability.

    Args:
        guard (Guard): The guard to evaluate the probability of.
    """
    guard: Guard


@dataclass(frozen=True)
class UnivariateMoment(Query):
    """Queries the PGA to obtain the n-th moment of a specified variable.

    Args:
        variable (str): The variable for which to compute the moment.
        moment (int): The order of the moment to compute.
    """
    variable: str
    moment: int


@dataclass(frozen=True)
class MixedMoment(Query):
    """Queries the PGA to obtain the (1,1)-order mixed moment of two specified variables.

    Args:
        variable1 (str): The first variable for which to compute the mixed moment.
        variable2 (str): The second variable for which to compute the mixed moment.
    """
    variable1: str
    variable2: str

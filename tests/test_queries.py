from fractions import Fraction

from symengine import Rational

from automata_inference.automata.factory import PGAFactory
from automata_inference.parser.ast.guards import Equals
from automata_inference.parser.ast.queries import (
    MixedMoment,
    PosteriorProbability,
    UnivariateMoment,
)
from automata_inference.programs.handlers.query_handler import QueryHandler

evaluate_query = QueryHandler.evaluate_query

# TODO add more complicated tests


def test_posterior_probability_query():
    pga = PGAFactory.bernoulli("X", Rational(1, 2))

    result = evaluate_query(PosteriorProbability(Equals("X", 1)), pga)

    assert result == Fraction(1, 2)


def test_univariate_first_moment_query():
    pga = PGAFactory.dirac("X", 2)

    result = evaluate_query(UnivariateMoment("X", 1), pga)

    assert result == 2

    pga = PGAFactory.geometric("Y", Rational(1, 2))

    result = evaluate_query(UnivariateMoment("Y", 1), pga)

    assert result == 1


def test_univariate_second_moment_query():
    pga = PGAFactory.dirac("X", 2)

    result = evaluate_query(UnivariateMoment("X", 2), pga)

    assert result == 4


def test_mixed_moment_query():
    pga = PGAFactory.dirac("X", 1).concat(PGAFactory.dirac("Y", 1))

    result = evaluate_query(MixedMoment("X", "Y"), pga)

    assert result == 1

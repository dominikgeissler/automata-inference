from fractions import Fraction

from symengine import Rational

from automata_inference.automata.factory import PGAFactory
from automata_inference.parser.ast.guards import Equals, LessThan
from automata_inference.parser.ast.queries import (
    MixedMoment,
    PosteriorProbability,
    UnivariateMoment,
)
from automata_inference.programs.handlers.query_handler import QueryHandler

evaluate_query = QueryHandler.evaluate_query

def test_posterior_probability_query():
    pga = PGAFactory.bernoulli("X", Rational(1, 2))

    result = evaluate_query(PosteriorProbability(Equals("X", 1)), pga)

    assert result == Fraction(1, 2)


def test_posterior_probability_query_with_threshold():
    pga = PGAFactory.geometric("X", Rational(1, 2))

    result = evaluate_query(PosteriorProbability(LessThan("X", 2)), pga)

    assert result == Fraction(3, 4)


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


def test_univariate_second_moment_query_for_geometric_distribution():
    pga = PGAFactory.geometric("X", Rational(1, 2))

    result = evaluate_query(UnivariateMoment("X", 2), pga)

    assert result == 3


def test_univariate_moment_query_on_weighted_union():
    pga = PGAFactory.dirac("X", 1).weighted_union(
        PGAFactory.dirac("X", 2), Rational(1, 4), Rational(3, 4)
    )

    result = evaluate_query(UnivariateMoment("X", 2), pga)

    assert result == Fraction(13, 4)


def test_mixed_moment_query():
    pga = PGAFactory.dirac("X", 1).concat(PGAFactory.dirac("Y", 1))

    result = evaluate_query(MixedMoment("X", "Y"), pga)

    assert result == 1


def test_mixed_moment_query_for_independent_geometric_distributions():
    pga = PGAFactory.geometric("X", Rational(1, 2)).concat(
        PGAFactory.geometric("Y", Rational(1, 2))
    )

    result = evaluate_query(MixedMoment("X", "Y"), pga)

    assert result == 1

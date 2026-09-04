from fractions import Fraction
from symengine import Rational

import pytest

from automata_inference.automata.factory import PGAFactory, PGA, State, Transition


def test_probability_mass_one():
    """Computes the probability mass where the mass is equal to one."""
    aut = PGAFactory.geometric("X", Rational(3, 4))
    assert aut.get_probability_mass() == 1


def test_probability_mass_infeasible():
    """LES is infeasible, e.g. 'probabiliy mass' diverges."""
    # 'PGA' has to be construced by hand as the semantics preserves PGA property
    aut = PGA(
        states={State(0, 0)},
        transition_matrix={Transition(State(0, 0), State(0, 0), "X")},
        initial={(1, State(0, 0))},
        final={(1, State(0, 0))},
    )

    # LP is infeasible
    with pytest.raises(RuntimeError):
        aut.get_probability_mass()


# @pytest.mark.skip()
def test_probability_mass_zero():
    """Probability mass is equal to zero."""
    aut = PGAFactory.zero()
    assert aut.get_probability_mass() == 0


def test_probability_mass():
    """Probability mass is between zero and one."""
    aut = PGA(
        states={State(0, 0), State(0, 1)},
        transition_matrix={Transition(State(0, 0), State(0, 1), weight=Rational(1, 2))},
        initial={(1, State(0, 0))},
        final={(1, State(0, 1))},
    )
    assert aut.get_probability_mass() == Fraction(1, 2)

    aut = PGA(
        states={State(0, 0), State(0, 1)},
        transition_matrix={Transition(State(0, 0), State(0, 1), weight=Rational(1, 2))},
        initial={(Rational(3, 8), State(0, 0))},
        final={(Rational(2, 3), State(0, 1))},
    )

    assert aut.get_probability_mass() == Fraction(1, 8)

    aut = PGA(
        states={State(0, 0), State(0, 1)},
        transition_matrix={Transition(State(0, 0), State(0, 1), weight=Rational(1, 3))},
        initial={(2, State(0, 0))},
        final={(1, State(0, 1))},
    )

    assert aut.get_probability_mass() == Fraction(2, 3)


def test_exact_results_for_symbolic_solution():
    aut = PGA(
        states={State(0, 0), State(0, 1)},
        transition_matrix={Transition(State(0, 0), State(0, 1), weight=Rational(1, 3))},
        initial={(1, State(0, 0))},
        final={(1, State(0, 1))},
    )

    aut2 = PGA(
        states={State(0, 0), State(0, 1)},
        transition_matrix={
            Transition(
                State(0, 0),
                State(0, 1),
                weight=Rational(3333333333333333, 10000000000000000),
            )
        },
        initial={(1, State(0, 0))},
        final={(1, State(0, 1))},
    )
    assert aut.get_probability_mass() != aut2.get_probability_mass()

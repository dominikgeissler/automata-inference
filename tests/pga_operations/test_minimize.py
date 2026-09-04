from symengine import Rational

from automata_inference.automata.factory import PGAFactory
from automata_inference.automata.model import PGA, State, Transition
from automata_inference.automata.operations.minimization import (
    remove_noncoaccessible_states,
)
from tests.utils import AutomatonTestUtils

create_pga = AutomatonTestUtils.create_pga
assert_equal_pga = AutomatonTestUtils.assert_equal_pga


def test_remove_non_coaccessible_states_no_change():
    """If no state is unreachable, nothing should change."""
    aut = PGAFactory.geometric("X", Rational(1, 2))
    expected = aut
    assert_equal_pga(expected, remove_noncoaccessible_states(aut))


def test_remove_non_coaccessible_states_changes():
    """If states are unreachable or non-coaccessible, they should be removed (alongside with the transitions)."""
    aut = create_pga(
        0,
        5,
        [(0, 2, None, 1), (0, 1, None, 1), (3, 2, None, 1), (4, 4, None, 1)],
        [(1, 0)],
        [(1, 2)],
    )
    expected = PGA(
        {State(0, 0), State(0, 2)},
        {Transition(State(0, 0), State(0, 2))},
        {(1, State(0, 0))},
        {(1, State(0, 2))},
    )
    assert_equal_pga(expected, actual=remove_noncoaccessible_states(aut))


def test_remove_non_coaccessible_states_remove_initial_states():
    """Edge case 1: Initial states have weight 0"""
    # Explicit zero as weight
    aut1 = create_pga(
        0, 3, [(0, 2, None, 1), (1, 2, None, 1)], [(0, 0), (1, 1)], [(1, 2)]
    )

    # Missing entry
    aut2 = create_pga(0, 3, [(0, 2, None, 1), (1, 2, None, 1)], [(1, 1)], [(1, 2)])

    expected = PGA(
        {State(0, 1), State(0, 2)},
        {Transition(State(0, 1), State(0, 2))},
        {(1, State(0, 1))},
        {(1, State(0, 2))},
    )

    assert_equal_pga(expected, remove_noncoaccessible_states(aut1))
    assert_equal_pga(expected, remove_noncoaccessible_states(aut2))


def test_remove_non_coaccessible_states_remove_final_states():
    """Edge case 2: Final states have weight 0"""
    # Explicit zero as weight
    aut1 = create_pga(
        0, 3, [(0, 1, None, 1), (0, 2, None, 1)], [(1, 0)], [(0, 1), (1, 2)]
    )

    # Missing entry
    aut2 = create_pga(0, 3, [(0, 1, None, 1), (0, 2, None, 1)], [(1, 0)], [(1, 2)])

    expected = PGA(
        {State(0, 0), State(0, 2)},
        {Transition(State(0, 0), State(0, 2))},
        {(1, State(0, 0))},
        {(1, State(0, 2))},
    )

    assert_equal_pga(expected, remove_noncoaccessible_states(aut1))
    assert_equal_pga(expected, remove_noncoaccessible_states(aut2))


def test_remove_everything():
    """If everything is removed, the zero-subdistribution PGA should be returned"""

    # No final state reachable
    aut1 = create_pga(
        0, 3, [(0, 1, "X", 1), (1, 0, "Y", Rational(1, 2))], [(1, 0)], [(1, 2)]
    )

    # No initial state reachable
    aut2 = create_pga(
        0, 3, [(1, 2, "X", 1), (2, 1, "Y", Rational(1, 2))], [(1, 0)], [(1, 2)]
    )

    actual1 = remove_noncoaccessible_states(aut1)
    actual2 = remove_noncoaccessible_states(aut2)

    # We expect the "zero"-PGA
    assert (
        len(actual1.states) == len(actual2.states) == 1
    ), "Only one state should remain."
    assert (
        len(actual1.transition_matrix) == len(actual2.transition_matrix) == 0
    ), "No transitions should be present."
    assert (
        len(actual1.final) == len(actual2.final) == 0
    ), "No final states should be present."

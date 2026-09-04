from symengine import Rational

from automata_inference.automata.model import PGA, State, Transition
from tests.utils import AutomatonTestUtils

make_pga = AutomatonTestUtils.create_pga
assert_pgas_equal = AutomatonTestUtils.assert_equal_pga


def test_concat_same_var():
    """Just some concatenation"""
    aut1 = make_pga(1, 2, [(0, 1, "X", 1)], {(1, 0)}, {(1, 1)})
    aut2 = make_pga(2, 2, [(0, 1, "X", 1)], {(1, 0)}, {(1, 1)})
    expected = PGA(
        {State(1, 0), State(1, 1), State(2, 0), State(2, 1)},
        {
            Transition(State(1, 0), State(1, 1), "X"),
            Transition(State(2, 0), State(2, 1), "X"),
            Transition(State(1, 1), State(2, 0)),
        },
        {(1, State(1, 0))},
        {(1, State(2, 1))},
    )
    assert_pgas_equal(expected, aut1.concat(aut2))


def test_concat_different_var():
    """Both automata have disjoint variables."""
    aut1 = make_pga(1, 2, [(0, 1, "Y", 1)], {(1, 0)}, {(1, 1)})
    aut2 = make_pga(2, 2, [(0, 1, "X", 1)], {(1, 0)}, {(1, 1)})
    expected = PGA(
        {State(1, 0), State(1, 1), State(2, 0), State(2, 1)},
        {
            Transition(State(1, 0), State(1, 1), "Y"),
            Transition(State(2, 0), State(2, 1), "X"),
            Transition(State(1, 1), State(2, 0)),
        },
        {(1, State(1, 0))},
        {(1, State(2, 1))},
    )
    assert_pgas_equal(expected, aut1.concat(aut2))


def test_concat_multiple_final_states_first():
    """First automaton has multiple final states"""
    aut1 = make_pga(
        1,
        3,
        [(0, 1, "Y", Rational(1, 2)), (0, 2, "X", Rational(1, 2))],
        {(1, 0)},
        {(1, 1), (1, 2)},
    )
    aut2 = make_pga(2, 2, [(0, 1, "X", 1)], {(1, 0)}, {(1, 1)})
    expected = PGA(
        {State(1, 0), State(1, 1), State(1, 2), State(2, 0), State(2, 1)},
        {
            Transition(State(1, 0), State(1, 1), "Y", Rational(1, 2)),
            Transition(State(1, 0), State(1, 2), "X", Rational(1, 2)),
            Transition(State(2, 0), State(2, 1), "X"),
            Transition(State(1, 1), State(2, 0)),
            Transition(State(1, 2), State(2, 0)),
        },
        {(1, State(1, 0))},
        {(1, State(2, 1))},
    )
    assert_pgas_equal(expected, aut1.concat(aut2))


def test_concat_multiple_final_states_last():
    """Last automaton has multiple final states"""
    aut1 = make_pga(1, 2, [(0, 1, "X", 1)], {(1, 0)}, {(1, 1)})
    aut2 = make_pga(
        2,
        3,
        [(0, 1, "Y", Rational(1, 2)), (0, 2, "X", Rational(1, 2))],
        {(1, 0)},
        {(1, 1), (1, 2)},
    )
    expected = PGA(
        {State(1, 0), State(1, 1), State(2, 0), State(2, 1), State(2, 2)},
        {
            Transition(State(1, 0), State(1, 1), "X"),
            Transition(State(2, 0), State(2, 1), "Y", Rational(1, 2)),
            Transition(State(2, 0), State(2, 2), "X", Rational(1, 2)),
            Transition(State(1, 1), State(2, 0)),
        },
        {(1, State(1, 0))},
        {(1, State(2, 1)), (1, State(2, 2))},
    )
    assert_pgas_equal(expected, aut1.concat(aut2))


def test_concat_multiple_initial_states_first():
    """First automaton has multiple initial states."""
    aut1 = make_pga(
        1,
        3,
        [(0, 2, "X", Rational(1, 2)), (1, 2, "X", Rational(1, 2))],
        {(1, 0), (1, 1)},
        {(1, 2)},
    )
    aut2 = make_pga(2, 1, [], {(1, 0)}, {(1, 0)})
    expected = PGA(
        {State(1, 0), State(1, 1), State(1, 2), State(2, 0)},
        {
            Transition(State(1, 0), State(1, 2), "X", Rational(1, 2)),
            Transition(State(1, 1), State(1, 2), "X", Rational(1, 2)),
            Transition(State(1, 2), State(2, 0)),
        },
        {(1, State(1, 0)), (1, State(1, 1))},
        {(1, State(2, 0))},
    )
    assert_pgas_equal(expected, aut1.concat(aut2))


def test_concat_multiple_initial_states_last():
    """Last automaton has multiple initial states."""
    aut1 = make_pga(1, 1, [], {(1, 0)}, {(1, 0)})
    aut2 = make_pga(
        2,
        3,
        [(0, 2, "X", Rational(1, 2)), (1, 2, "X", Rational(1, 2))],
        {(1, 0), (1, 1)},
        {(1, 2)},
    )
    expected = PGA(
        {State(1, 0), State(2, 0), State(2, 1), State(2, 2)},
        {
            Transition(State(2, 0), State(2, 2), "X", Rational(1, 2)),
            Transition(State(2, 1), State(2, 2), "X", Rational(1, 2)),
            Transition(State(1, 0), State(2, 0)),
            Transition(State(1, 0), State(2, 1)),
        },
        {(1, State(1, 0))},
        {(1, State(2, 2))},
    )
    assert_pgas_equal(expected, aut1.concat(aut2))

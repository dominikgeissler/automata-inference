from symengine import Rational

from automata_inference.automata.model import (
    PGA,
    State,
    Transition,
    ProductState,
    current_state_namespace,
)
from tests.utils import AutomatonTestUtils

create_pga = AutomatonTestUtils.create_pga
assert_equal_pga = AutomatonTestUtils.assert_equal_pga


def to_product_state(left: int, right: int, right_namespace: int = 0):
    return ProductState(State(1, left), State(right_namespace, right))


def test_decrement_no_change():
    """No transition with the requested indeterminate."""
    aut = create_pga(0, 1, [(0, 0, "Y", Rational(1, 2))], {(1, 0)}, {(1, 0)})
    expected = PGA(
        {State(0, 0), State(1, 0)},
        {Transition(State(0, 0), State(0, 0), "Y", Rational(1, 2))},
        {(1, State(0, 0)), (1, State(1, 0))},
        {(1, State(0, 0))},
    )
    assert_equal_pga(expected, aut.decrement("X"))


def test_decrement_no_branching():
    aut = create_pga(1, 2, [(0, 1, "X", Rational(1, 2))], [(1, 0)], [(2, 1)])
    right_namespace = current_state_namespace() + 1
    # Shorthands for the states
    # Note that the 'right' state has namespace '0' as we assume this to be dynamically assigned by the program
    p00 = to_product_state(0, 0, right_namespace)
    p11 = to_product_state(1, 1, right_namespace)

    expected = PGA(
        {p00, p11},
        {Transition(p00, p11, weight=Rational(1, 2))},
        {(1, p00)},
        {(2, p11)},
    )

    assert_equal_pga(expected, aut.decrement("X"))


def test_decrement_multiple_branches():
    aut = create_pga(
        1,
        6,
        [
            (0, 1, "X", Rational(1, 2)),
            (2, 3, "X", Rational(1, 4)),
            (4, 5, None, Rational(2, 3)),
        ],
        [(1, 0), (1, 2), (1, 4)],
        [(1, 1), (1, 3), (1, 5)],
    )

    right_namespace = current_state_namespace() + 1

    p00 = to_product_state(0, 0, right_namespace)
    p11 = to_product_state(1, 1, right_namespace)
    p20 = to_product_state(2, 0, right_namespace)
    p31 = to_product_state(3, 1, right_namespace)
    s4 = State(1, 4)
    s5 = State(1, 5)

    expected = PGA(
        {p00, p11, p20, p31, s4, s5},
        {
            Transition(p00, p11, weight=Rational(1, 2)),
            Transition(p20, p31, weight=Rational(1, 4)),
            Transition(s4, s5, weight=Rational(2, 3)),
        },
        {(1, p00), (1, p20), (1, s4)},
        {(1, p11), (1, p31), (1, s5)},
    )

    assert_equal_pga(expected, aut.decrement("X"))


def test_decrement_self_loop():
    aut = create_pga(
        1, 1, [(0, 0, "Y", Rational(1, 2))], [(1, 0)], [(Rational(1, 2), 0)]
    )

    right_namespace = current_state_namespace() + 1

    p00 = to_product_state(0, 0, right_namespace)
    p01 = to_product_state(0, 1, right_namespace)
    s0 = State(1, 0)

    expected = PGA(
        {p00, p01, s0},
        {
            Transition(p01, p01, "Y", Rational(1, 2)),
            Transition(p00, p01, weight=Rational(1, 2)),
        },
        {(1, p00), (1, s0)},
        {(Rational(1, 2), p01), (Rational(1, 2), s0)},
    )

    assert_equal_pga(expected, aut.decrement("Y"))

from symengine import Rational

from automata_inference.automata.model import DFA, State, Transition, PGA, ProductState
from tests.utils import AutomatonTestUtils

create_pga = AutomatonTestUtils.create_pga
assert_equal_pga = AutomatonTestUtils.assert_equal_pga


def test_product_true():
    """Filters nothing"""
    
    aut = create_pga(0, 3, [(0, 1, "X", Rational(1, 2)), (0, 2, "Y", Rational(1,2))], [(1, 0)], [(1,1), (1,2)])
    
    # Models "true"
    dfa = DFA(
        {State(1, 0)},
        [Transition(State(1,0), State(1,0), symbol) for symbol in {"X", "Y"}],
        {State(1,0)},
        {State(1,0)}
    )
    
    expected = PGA(
        {ProductState(State(0, 0), State(1,0)), ProductState(State(0,1), State(1,0)), ProductState(State(0,2), State(1,0))},
        [
            Transition(ProductState(State(0, 0), State(1,0)), ProductState(State(0,1), State(1,0)), "X", Rational(1,2)),
            Transition(ProductState(State(0, 0), State(1,0)), ProductState(State(0,2), State(1,0)), "Y", Rational(1,2))
        ],
        {(1, ProductState(State(0, 0), State(1,0)))},
        {(1, ProductState(State(0,1), State(1,0))), (1, ProductState(State(0,2), State(1,0)))},
    )  # Nothing is filtered
    
    assert_equal_pga(expected, aut.filter(dfa))


def test_product_false():
    """Filters everything."""
    aut = create_pga(0, 3, [(0, 1, "X", Rational(1, 2)), (0, 2, "Y", Rational(1,2))], [(1, 0)], [(1,1), (1,2)])
    
    # Models "false"
    dfa = DFA(
            {State(1, 0)},
            [Transition(State(1,0), State(1,0), symbol) for symbol in {"X", "Y"}],
            {State(1,0)},
            {}
        )
    
    actual = aut.filter(dfa)
    
    # We expect the "zero"-PGA
    assert len(actual.states) == 1, "Only one state should remain."
    assert len(actual.transition_matrix) == 0, "No transitions should be present."
    assert len(actual.final) == 0, "No final states should be present."

def test_product_filter():
    """Filters something."""
    
    # Geometric distribution in X (with parameter 1/2)
    aut = create_pga(
        0, 1, [(0,0,"X", Rational(1,2))],[(1, 0)], [(Rational(1,2), 0)]
    )
    
    s,t1, t2 = State(0, 0), State(1, 0), State(1,1)
    
    # Models "x mod 2 = 1"
    dfa = DFA(
        {t1, t2},
        [Transition(t1, t2, "X"), Transition(t2, t1, "X")],
        {t1},
        {t2}
    )
    
    p1 = ProductState(s, t1)
    p2 = ProductState(s, t2)
    
    expected = PGA(
        {p1, p2},
        [Transition(p1, p2, "X", Rational(1,2)), Transition(p2, p1, "X", Rational(1,2))],
        {(1, p1)},
        {(Rational(1,2), p2)}
    )
    
    assert_equal_pga(expected, aut.filter(dfa))
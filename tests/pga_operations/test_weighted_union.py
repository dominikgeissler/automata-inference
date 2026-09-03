from symengine import Rational

from automata_inference.automata.model import PGA, State, Transition
from tests.utils import AutomatonTestUtils

create_pga = AutomatonTestUtils.create_pga
assert_equal_pga = AutomatonTestUtils.assert_equal_pga


def test_weighted_union_parameter_zero():
    """Atleast one parameter is zero."""
    aut1 = create_pga(0, 2, [(0, 1, "Y", 1)], [(1, 0)], [(1, 1)])
    aut2 = create_pga(1, 2, [(0, 1, "X", 1)], [(1, 0)], [(1, 1)])

    # Left side has weight 0, right has weight one
    expected = PGA(
        {State(0, 0), State(0, 1), State(1, 0), State(1,1)},
        [
            Transition(State(0,0), State(0, 1), "Y", 1),
            Transition(State(1,0), State(1, 1), "X", 1)    
        ],
        {(0, State(0, 0)), (1, State(1,0))},
        {(1, State(0, 1)), (1, State(1,1))}
    )
    assert_equal_pga(expected, aut1.weighted_union(aut2, 0, 1))


def test_weighted_union():
    """Both parameters are different from zero"""
    aut1 = create_pga(0, 2, [(0, 1, "Y", 1)], [(1, 0)], [(1, 1)])
    aut2 = create_pga(1, 2, [(0, 1, "X", 1)], [(1, 0)], [(1, 1)])
    
    p = Rational(2,5)
    q = Rational(3,5)
    
    expected = PGA(
            {State(0, 0), State(0, 1), State(1, 0), State(1,1)},
            [
                Transition(State(0,0), State(0, 1), "Y", 1),
                Transition(State(1,0), State(1, 1), "X", 1)    
            ],
            {(Rational(2,5), State(0, 0)), (Rational(3,5), State(1,0))},
            {(1, State(0, 1)), (1, State(1,1))}
        )
    
    assert_equal_pga(expected, aut1.weighted_union(aut2, p, q))
    
    # Swap the order
    expected = PGA(
                {State(0, 0), State(0, 1), State(1, 0), State(1,1)},
                [
                    Transition(State(0,0), State(0, 1), "Y", 1),
                    Transition(State(1,0), State(1, 1), "X", 1)    
                ],
                {(Rational(3,5), State(0, 0)), (Rational(2,5), State(1,0))},
                {(1, State(0, 1)), (1, State(1,1))}
            )
    
    assert_equal_pga(expected, aut1.weighted_union(aut2, q, p))
from symengine import Rational

from automata_inference.automata.factory import PGAFactory
from automata_inference.automata.model import PGA, IndexedState, State, Transition
from tests.utils import AutomatonTestUtils

create_pga = AutomatonTestUtils.create_pga
assert_equal_pga = AutomatonTestUtils.assert_equal_pga


def test_transition_substitution_no_change():
    """Nothing changes"""
    aut = PGAFactory.geometric("X", Rational(1, 2))
    subs = PGAFactory.geometric("Y", Rational(1, 4))
    assert_equal_pga(aut, aut.transition_substitution("Y", subs))
    
    
def test_transition_substitution_changes_path():
    """Some changes are made on a path"""
    aut = create_pga(0, 2, [(0, 1, "X", Rational(1,3))], [(1,0)], [(1,1)])
    
    subs = create_pga(
        1, 1, [(0,0,"X", Rational(1,2))],[(1, 0)], [(Rational(1,2), 0)]
    )
    s0, s1 = State(0,0), State(0,1) 
    q1 = IndexedState(State(1,0), 0)
    
    expected = PGA(
        {s0, s1, q1},
        [Transition(s0, q1, weight=Rational(1,3)), Transition(q1, q1, "X", Rational(1,2)), Transition(q1, s1, weight=Rational(1,2))],
        {(1, s0)},
        {(1, s1)}
    )

    assert_equal_pga(expected, aut.transition_substitution("X", subs))


def test_transition_substitution_zero_pga():
    """Substitutes by a PGA with behavior '0'."""
    aut = create_pga(0, 1, [(0, 0, "X", Rational(1,3))], [(1,0)], [(Rational(2,3),0)])
        
    # Zero PGA
    subs = create_pga(1, 1, [], [(1,0)], [])
    
    s1 = State(0, 0)
    t = IndexedState(State(1,0), 0)
    expected = PGA(
        {s1, t},
        [Transition(s1, t, weight=Rational(1,3))],
        {(1, s1)},
        {(Rational(2,3), s1)}
    )
    assert_equal_pga(expected, aut.transition_substitution("X", subs))
        

def test_transition_substitution_one_pga():
    """Substitutes by a PGA with behavior '1'."""
    aut = create_pga(0, 2, [(0, 1, "X", Rational(1,3))], [(1,0)], [(Rational(2,3),1)])
        
    # Zero PGA
    subs = create_pga(1, 1, [], [(1,0)], [(1,0)])
    
    s1 = State(0, 0)
    s2 = State(0, 1)
    t = IndexedState(State(1,0), 0)
    expected = PGA(
        {s1, s2, t},
        [Transition(s1, t, weight=Rational(1,3)), Transition(t, s2)],
        {(1, s1)},
        {(Rational(2,3), s2)}
    )
    assert_equal_pga(expected, aut.transition_substitution("X", subs))
        

def test_transition_substitution_loop():
    """Substitutes a loop."""
    # Substitute by geometric distribution
    aut = create_pga(0, 1, [(0, 0, "X", Rational(1,3))], [(1,0)], [(Rational(2,3),0)])
    subs = create_pga(1, 1, [(0, 0, "Y", Rational(3,4))], [(1,0)], [(Rational(1,4),0)])
    
    s = State(0,0)
    t = IndexedState(State(1,0), 0)
    
    expected = PGA(
        {s, t},
        [Transition(s, t, weight=Rational(1,3)), Transition(t, t, "Y", Rational(3,4)), Transition(t, s, weight=Rational(1,4))],
        {(1, s)},
        {(Rational(2,3), s)}
    )
    
    assert_equal_pga(expected, aut.transition_substitution("X", subs))



def test_transition_substitution_multiple_transitions():
    from automata_inference.visualization.graphviz import visualize
    
    aut = create_pga(0, 3, [(0, 0, "X", Rational(1,2)), (0, 1, "X", Rational(1,2)), (1,2,"Y", 1)], [(1,0)], [(1,2)])
    subs = create_pga(1, 2, [(0, 0, "X", Rational(1,3)), (0, 1, "Z", 1)], [(1,0)], [(Rational(2,3),1)])
    visualize(aut, out_path="aut")
    visualize(subs, out_path="subs")
    s1, s2, s3 = State(0, 0), State(0, 1), State(0, 2)
    t11, t12, t21, t22 = IndexedState(State(1,0), 0), IndexedState(State(1,1), 0), IndexedState(State(1,0), 1), IndexedState(State(1,1), 1)
    
    expected = PGA(
        {s1, s2, s3, t11, t12, t21, t22},
        [
            Transition(s1, t11, weight=Rational(1,2)), Transition(t11, t11, "X", Rational(1,3)), Transition(t11, t12, "Z"),
            Transition(t12, s1, weight=Rational(2,3)), Transition(s1, t21, weight=Rational(1,2)), Transition(t21, t21, "X", Rational(1,3)), Transition(t21, t22, "Z"),
            Transition(t22, s2, weight=Rational(2,3)), Transition(s2, s3, "Y")
        ],
        {(1, s1)},
        {(1,s3)}
    )
    visualize(expected, out_path="expected")
    visualize(aut.transition_substitution("X", subs), out_path="actual")
    assert_equal_pga(expected, aut.transition_substitution("X", subs))
    

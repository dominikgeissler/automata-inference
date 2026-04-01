from automata_inference.automata_factory import PGAFactory, PGA
import symengine as se
import pytest
from fractions import Fraction

def test_probability_mass_one():
    """Computes the probability mass where the mass is equal to one."""
    aut = PGAFactory.geometric("X", se.Rational(3,4), {"X", "1"})
    assert aut.get_probability_mass_lin_eq() == 1
    M = se.Matrix(aut._construct_marginalized_transition_matrix(sorted(aut.states)))
    print(se.eye(M.rows) - M)
    assert False

@pytest.mark.skip()
def test_probability_mass_infeasible():
    """LP is infeasible, e.g. 'probabiliy mass' diverges."""
    # 'PGA' has to be construced by hand as the semantic preserves PGA property
    aut = PGA(
        states={"q0"},
        transition_matrix={"1": [(1, "q0", "q0")]},
        initial={("1", "q0")},
        final={("1", "q0")},
    )
    
    # LP is infeasible
    with pytest.raises(ValueError):
        aut.get_probability_mass_lin_eq()

# @pytest.mark.skip()
def test_probability_mass_zero():
    """Probability mass is equal to zero."""
    aut = PGA(
        states={"q0"},
        transition_matrix={"1": [(1, "q0", "q0")]},
        initial={("1", "q0")},
        final={},
    )
    M = se.Matrix(aut._construct_marginalized_transition_matrix(["q0"]))
    print(se.eye(M.rows) - M)
    assert aut.get_probability_mass_lin_eq() == 0

def test_probability_mass():
    """Probability mass is between zero and one."""
    aut = PGA(
        states={"q0", "q1"},
        transition_matrix={"1": [(se.Rational(1,2), "q0", "q1")]},
        initial={(1, "q0")},
        final={(1, "q1")}
    )
    assert aut.get_probability_mass_lin_eq() == Fraction(1,2)
    
    aut = PGA(
        states={"q0", "q1"},
        transition_matrix={"1": [(se.Rational(1,2), "q0", "q1")]},
        initial={(se.Rational(3,8), "q0")},
        final={(se.Rational(2,3), "q1")}
    )
    
    assert aut.get_probability_mass_lin_eq() == Fraction(1,8)
    
    aut = PGA(
        states={"q0", "q1"},
        transition_matrix={"1": [(se.Rational(1,3), "q0", "q1")]},
        initial={(1, "q0")},
        final={(1, "q1")}
    )
    
    assert aut.get_probability_mass_lin_eq() == Fraction(1,3)
    

#s@pytest.mark.skip(reason="This should pass if the LP solution is symbolic.")
def test_this_should_pass_at_some_point():
    aut = PGA(
        states={"q0", "q1"},
        transition_matrix={"1": [(se.Rational(1,3), "q0", "q1")]},
        initial={(1, "q0")},
        final={(1, "q1")}
    )
    
    aut2 = PGA(
        states={"q0", "q1"},
        transition_matrix={"1": [(se.Rational(3333333333333333,10000000000000000), "q0", "q1")]},
        initial={(1, "q0")},
        final={(1, "q1")}
    )
    assert aut.get_probability_mass_lin_eq() != aut2.get_probability_mass_lin_eq()
    
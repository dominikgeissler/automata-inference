from automata_inference.automata_factory import minimize, PGAFactory, PGA
from automata_inference.program_context import ProgramContext
from symengine import Rational
from tests.utils import compare_dicts_with_unordered_lists

def test_weighted_union_parameter_zero():
    """Atleast one parameter is zero."""
    context = ProgramContext({"X", "Y", "1"})
    aut1 = PGAFactory.dirac("X", 3, context.indeterminates)
    aut2 = PGAFactory.geometric("Y", Rational(1,3), context.indeterminates)

    # Left side has weight 0, right has weight one
    actual = minimize(aut1.weighted_union(aut2, 0, 1), context.indeterminates)
    # Changes here because i change the second automaton in resolve_conflict
    expected = PGA(
        {"q_0_1"},
        {
            "X": [],
            "Y": [(Rational(2,3), "q_0_1", "q_0_1")],
            "1": [],
        },
        {(Rational(1,1), "q_0_1")},
        {(Rational(1,3), "q_0_1")}
    )

    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )
    
    # Right side has weight 0, left has weight one
    actual = minimize(aut1.weighted_union(aut2, 1, 0), context.indeterminates)
    expected = aut1

    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )
    
    actual = minimize(aut1.weighted_union(aut2, 0, 0), context.indeterminates)
    expected = PGAFactory.zero(context.indeterminates)
    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )


def test_weighted_union():
    """Both parameters are different from zero"""
    context = ProgramContext({"X", "Y", "1"})
    aut1 = PGAFactory.dirac("X", 2, context.indeterminates)
    aut2 = PGAFactory.geometric("Y", Rational(1,3), context.indeterminates)
    
    p = Rational(2,5)
    q = Rational(3,5)
    
    expected = PGA(
        {"q_0", "q_1", "q_2", "q_0_1"},
        {
            "X": [(1, "q_0", "q_1"), (1, "q_1", "q_2")],
            "Y": [(Rational(2,3), "q_0_1", "q_0_1")],
            "1": []
        },
        {(Rational(2,5), "q_0"), (Rational(3,5), "q_0_1")},
        {(1, "q_2"), (Rational(1,3), "q_0_1")}
    )
    
    actual = aut1.weighted_union(aut2, p, q)
    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )
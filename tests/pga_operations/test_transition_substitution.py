from symengine import Rational
from automata_inference.automata_factory import PGAFactory, PGA, minimize
from automata_inference.program_context import ProgramContext
from tests.utils import compare_dicts_with_unordered_lists


def test_transition_substitution_no_change():
    """Nothing changes"""
    context = ProgramContext({"X", "Y", "1"})
    aut = PGAFactory.geometric("X", Rational(1, 2), context.indeterminates)
    subs = PGAFactory.geometric("Y", Rational(1, 4), context.indeterminates)
    expected = aut
    actual = aut.transition_substitution("Y", subs)
    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )
    
def test_transition_substitution_changes_path():
    """Some changes are made on a path"""
    context = ProgramContext({"X", "Y", "1"})
    aut = PGAFactory.dirac("X", 1, context.indeterminates)
    subs = PGAFactory.geometric("Y", Rational(1,2), context.indeterminates)

    expected = PGA(
        {"q_0", "q_1", "q_0_1_0"},
        {
            "X": [],
            "Y": [(Rational(1,2), "q_0_1_0", "q_0_1_0")],
            "1": [(Rational(1,1), "q_0", "q_0_1_0"), (Rational(1,2), "q_0_1_0", "q_1")]
        },
        {(Rational(1,1), "q_0")},
        {(Rational(1,1), "q_1")}
    )
    actual = aut.transition_substitution("X", subs)
    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )


def test_transition_substitution_changes_loop():
    """Some changes are made in the loop."""
    # Substitute by zero-DFA
    # Should be equivalent to A[X/0]
    context = ProgramContext({"X", "1"})
    aut = PGAFactory.geometric("X", Rational(1, 2), context.indeterminates)
    subs = PGAFactory.zero(context.indeterminates)
    expected = PGA({"q_0"}, {"X": [],  "1": []}, {(Rational(1, 1), "q_0")}, {(Rational(1, 2), "q_0")})
    actual = minimize(aut.transition_substitution("X", subs), context.indeterminates)

    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )

    # Substitute by one DFA
    # Should be equivalent to A[X/1]
    aut = PGAFactory.geometric("X", Rational(1, 2), context.indeterminates)
    subs = PGAFactory.one(context.indeterminates)
    expected = PGA(
        {"q_0", "q_0_1_0"},
        {"X": [], "1": [(Rational(1, 2), "q_0", "q_0_1_0"), (Rational(1, 1), "q_0_1_0", "q_0")]},
        {(Rational(1, 1), "q_0")},
        {(Rational(1, 2), "q_0")},
    )
    actual = minimize(aut.transition_substitution("X", subs), context.indeterminates)
    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )

    # Substitute by geometric distribution
    context = ProgramContext({"X", "Y", "1"})
    aut = PGAFactory.geometric("X", Rational(1, 2), context.indeterminates)
    subs = PGAFactory.geometric("Y", Rational(1, 4), context.indeterminates)
    expected = PGA(
        {"q_0", "q_0_1_0"},
        {
            "X": [],
            "Y": [(Rational(3, 4), "q_0_1_0", "q_0_1_0")],
            "1": [(Rational(1, 2), "q_0", "q_0_1_0"), (Rational(1, 4), "q_0_1_0", "q_0")],
        },
        {(Rational(1, 1), "q_0")},
        {(Rational(1, 2), "q_0")},
    )
    actual = aut.transition_substitution("X", subs)
    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )

from symengine import Rational
from automata_inference.automata_factory import PGA, PGAFactory
from tests.utils import compare_dicts_with_unordered_lists


def test_decrement_no_change():
    """No transition with indeterminate present."""
    aut = PGAFactory.geometric("Y", Rational(1, 2))
    actual = aut.decrement("X")
    expected = PGA(
        {"q_0_1"},
        {"X": [], "Y": [(Rational(1, 2), "q_0_1", "q_0_1")], "Z": [], "1": []},
        {(Rational(1, 1), "q_0_1")},
        {(Rational(1, 2), "q_0_1")},
    )
    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )


def test_decrement_no_branching():
    """'Singular' branch with indeterminate present."""
    aut = PGAFactory.geometric("X", Rational(1, 2))
    actual = aut.decrement("X")
    expected = PGA(
        {"q_0", "(q_0,p_0)", "(q_0,p_1)"},
        {
            "X": [(Rational(1, 2), "(q_0,p_1)", "(q_0,p_1)")],
            "Y": [],
            "Z": [],
            "1": [(Rational(1, 2), "(q_0,p_0)", "(q_0,p_1)")],
        },
        {(Rational(1, 1), "q_0"), (Rational(1, 1), "(q_0,p_0)")},
        {(Rational(1, 2), "q_0"), (Rational(1, 2), "(q_0,p_1)")},
    )

    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )


def test_decrement_branching_no_constant():
    """Branching automaton, but the coefficient of X^0 is 0."""
    aut = PGA(
        {"q_0", "q_1", "q_2"},
        {"X": [(Rational(1, 2), "q_0", "q_1"), (Rational(1, 2), "q_0", "q_2")], "1": []},
        {(Rational(1, 1), "q_0")},
        {(Rational(1, 1), "q_1"), (Rational(1, 1), "q_2")},
    )

    expected = PGA(
        {"(q_0,p_0)", "(q_1,p_1)", "(q_2,p_1)"},
        {
            "X": [],
            "1": [(Rational(1, 2), "(q_0,p_0)", "(q_1,p_1)"), (Rational(1, 2), "(q_0,p_0)", "(q_2,p_1)")],
            "Z": [],
            "Y": [],
        },
        {(Rational(1, 1), "(q_0,p_0)")},
        {(Rational(1, 1), "(q_1,p_1)"), (Rational(1, 1), "(q_2,p_1)")},
    )
    actual = aut.decrement("X")

    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )

    aut = PGA(
        {"q_0", "q_1", "q_2", "q_3"},
        {
            "X": [(Rational(1, 2), "q_0", "q_1"), (Rational(1, 2), "q_0", "q_2"), (Rational(1, 1), "q_1", "q_3")],
            "1": [],
        },
        {(Rational(1, 1), "q_0")},
        {(Rational(1, 1), "q_3"), (Rational(1, 1), "q_2")},
    )
    expected = PGA(
        {"(q_0,p_0)", "(q_1,p_1)", "(q_2,p_1)", "(q_3,p_1)"},
        {
            "X": [(Rational(1, 1), "(q_1,p_1)", "(q_3,p_1)")],
            "1": [(Rational(1, 2), "(q_0,p_0)", "(q_1,p_1)"), (Rational(1, 2), "(q_0,p_0)", "(q_2,p_1)")],
            "Z": [],
            "Y": [],
        },
        {(Rational(1, 1), "(q_0,p_0)")},
        {(Rational(1, 1), "(q_3,p_1)"), (Rational(1, 1), "(q_2,p_1)")},
    )

    actual = aut.decrement("X")

    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )


def test_decrement_branching_constant():
    """Branching automaton, but the coefficient of X^0 is not 0."""
    aut = PGA(
        {"q_0", "q_1", "q_2"},
        {"X": [(Rational(1, 2), "q_0", "q_1"), (Rational(1, 2), "q_0", "q_2")], "1": []},
        {(Rational(1, 1), "q_0")},
        {(Rational(1, 1), "q_1"), (Rational(1, 1), "q_2"), (Rational(1, 2), "q_0")},
    )
    # FIXME why do we have only "X" and "1" as dictkeys here?
    expected = PGA(
        {"(q_0,p_0)", "(q_1,p_1)", "(q_2,p_1)", "q_0"},
        {
            "X": [],
            "1": [(Rational(1, 2), "(q_0,p_0)", "(q_1,p_1)"), (Rational(1, 2), "(q_0,p_0)", "(q_2,p_1)")],
        },
        {(Rational(1, 1), "(q_0,p_0)"), (Rational(1, 1), "q_0")},
        {(Rational(1, 1), "(q_1,p_1)"), (Rational(1, 1), "(q_2,p_1)"), (Rational(1, 2), "q_0")},
    )
    actual = aut.decrement("X")
    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )

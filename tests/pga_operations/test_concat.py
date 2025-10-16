from symengine import Rational
from automata_inference.automata_factory import PGA

from tests.utils import compare_dicts_with_unordered_lists


def test_concat_same_var():
    """Just some concatenation"""
    aut1 = PGA(
        {"q_0", "q_1"},
        {"X": [(Rational(1, 1), "q_0", "q_1")]},
        {(Rational(1, 1), "q_0")},
        {(Rational(1, 1), "q_1")},
    )
    aut2 = PGA(
        {"q_2", "q_3"},
        {"X": [(Rational(1, 1), "q_2", "q_3")]},
        {(Rational(1, 1), "q_2")},
        {(Rational(1, 1), "q_3")},
    )
    expected = PGA(
        {"q_0", "q_1", "q_2", "q_3"},
        {"X": [(Rational(1, 1), "q_0", "q_1"), (Rational(1, 1), "q_2", "q_3")], "1": [(Rational(1, 1), "q_1", "q_2")]},
        {(Rational(1, 1), "q_0")},
        {(Rational(1, 1), "q_3")},
    )
    actual = aut1.concat(aut2)
    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )


def test_concat_different_var():
    """Both automata have disjoint variables."""
    aut1 = PGA(
        {"q_0", "q_1"},
        {"Y": [(Rational(1, 1), "q_0", "q_1")], "X": []},
        {(Rational(1, 1), "q_0")},
        {(Rational(1, 1), "q_1")},
    )
    aut2 = PGA(
        {"q_2", "q_3"},
        {"X": [(Rational(1, 1), "q_2", "q_3")], "Y": []},
        {(Rational(1, 1), "q_2")},
        {(Rational(1, 1), "q_3")},
    )
    expected = PGA(
        {"q_0", "q_1", "q_2", "q_3"},
        {
            "X": [(Rational(1, 1), "q_2", "q_3")],
            "Y": [(Rational(1, 1), "q_0", "q_1")],
            "1": [(Rational(1, 1), "q_1", "q_2")],
        },
        {(Rational(1, 1), "q_0")},
        {(Rational(1, 1), "q_3")},
    )
    actual = aut1.concat(aut2)
    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )


def test_concat_multiple_final_states_first():
    """First automaton has multiple final states"""
    aut1 = PGA(
        {"q_0", "q_1", "q_2"},
        {"Y": [(Rational(1, 2), "q_0", "q_1")], "X": [(Rational(1, 2), "q_0", "q_2")]},
        {(Rational(1, 1), "q_0")},
        {(Rational(1, 1), "q_1"), (Rational(1, 1), "q_2")},
    )
    aut2 = PGA(
        {"q_3", "q_4"},
        {"X": [(Rational(1, 1), "q_3", "q_4")], "Y": []},
        {(Rational(1, 1), "q_3")},
        {(Rational(1, 1), "q_4")},
    )

    expected = PGA(
        {f"q_{i}" for i in range(5)},
        {
            "X": [(Rational(1, 2), "q_0", "q_2"), (Rational(1, 1), "q_3", "q_4")],
            "Y": [(Rational(1, 2), "q_0", "q_1")],
            "1": [(Rational(1, 1), "q_1", "q_3"), (Rational(1, 1), "q_2", "q_3")],
        },
        {(Rational(1, 1), "q_0")},
        {(Rational(1, 1), "q_4")},
    )

    actual = aut1.concat(aut2)
    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )


def test_concat_multiple_final_states_last():
    """Last automaton has multiple final states"""
    aut1 = PGA(
        {"q_0", "q_1"},
        {"X": [(Rational(1, 1), "q_0", "q_1")], "Y": []},
        {(Rational(1, 1), "q_0")},
        {(Rational(1, 1), "q_1")},
    )
    aut2 = PGA(
        {"q_2", "q_3", "q_4"},
        {"Y": [(Rational(1, 2), "q_2", "q_3")], "X": [(Rational(1, 2), "q_2", "q_4")]},
        {(Rational(1, 1), "q_2")},
        {(Rational(1, 1), "q_3"), (Rational(1, 1), "q_4")},
    )

    expected = PGA(
        {f"q_{i}" for i in range(5)},
        {
            "X": [(Rational(1, 1), "q_0", "q_1"), (Rational(1, 2), "q_2", "q_4")],
            "Y": [(Rational(1, 2), "q_2", "q_3")],
            "1": [(Rational(1, 1), "q_1", "q_2")],
        },
        {(Rational(1, 1), "q_0")},
        {(Rational(1, 1), "q_3"), (Rational(1, 1), "q_4")},
    )

    actual = aut1.concat(aut2)
    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )


def test_concat_multiple_initial_states_first():
    """First automaton has multiple initial states."""
    aut1 = PGA(
        {"q_0", "q_1", "q_2"},
        {"X": [(Rational(1, 2), "q_0", "q_2"), (Rational(1, 2), "q_1", "q_2")]},
        {(Rational(1, 1), "q_0"), (Rational(1, 1), "q_1")},
        {(Rational(1, 1), "q_2")},
    )

    aut2 = PGA({"q_3"}, {"X": []}, {(Rational(1, 1), "q_3")}, {(Rational(1, 1), "q_3")})

    expected = PGA(
        {f"q_{i}" for i in range(4)},
        {"X": [(Rational(1, 2), "q_0", "q_2"), (Rational(1, 2), "q_1", "q_2")], "1": [(Rational(1, 1), "q_2", "q_3")]},
        {(Rational(1, 1), "q_0"), (Rational(1, 1), "q_1")},
        {(Rational(1, 1), "q_3")},
    )

    actual = aut1.concat(aut2)

    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )


def test_concat_multiple_initial_states_last():
    """Last automaton has multiple initial states."""
    aut1 = PGA({"q_0"}, {"X": []}, {(Rational(1, 1), "q_0")}, {(Rational(1, 1), "q_0")})

    aut2 = PGA(
        {"q_1", "q_2", "q_3"},
        {"X": [(Rational(1, 2), "q_1", "q_3"), (Rational(1, 2), "q_2", "q_3")]},
        {(Rational(1, 1), "q_1"), (Rational(1, 1), "q_2")},
        {(Rational(1, 1), "q_3")},
    )

    expected = PGA(
        {f"q_{i}" for i in range(4)},
        {
            "X": [(Rational(1, 2), "q_1", "q_3"), (Rational(1, 2), "q_2", "q_3")],
            "1": [(Rational(1, 1), "q_0", "q_1"), (Rational(1, 1), "q_0", "q_2")],
        },
        {(Rational(1, 1), "q_0")},
        {(Rational(1, 1), "q_3")},
    )

    actual = aut1.concat(aut2)

    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )

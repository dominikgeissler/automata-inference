from symengine import Rational
from automata_inference.automata_factory import PGAFactory, remove_noncoaccessible_states, PGA
from tests.utils import compare_dicts_with_unordered_lists


def test_remove_non_coaccessible_states_no_change():
    """If no state is unreachable, nothing should change"""
    aut = PGAFactory.geometric("X", Rational(1, 2))
    expected = aut
    actual = remove_noncoaccessible_states(aut)
    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )


def test_remove_non_coaccessible_states_changes():
    """If states are unreachable or non-coaccessible, they should be removed"""
    aut = PGA(
        {"q_0", "q_1", "q_2", "q_3", "q_4"},
        {"1": [(1, "q_0", "q_2"), (1, "q_0", "q_1"), (1, "q_3", "q_2"), (1, "q_4", "q_4")]},
        {(1, "q_0")},
        {(1, "q_2")},
    )
    expected = PGA({"q_0", "q_2"}, {"1": [(1, "q_0", "q_2")]}, {(1, "q_0")}, {(1, "q_2")})
    actual = remove_noncoaccessible_states(aut)
    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )


def test_remove_non_coaccessible_states_remove_initial_states():
    """Edge case 1: Initial states have weight 0"""
    aut = PGA(
        {"q_0", "q_1", "q_2"}, {"1": [(1, "q_0", "q_2"), (1, "q_1", "q_2")]}, {(0, "q_0"), (1, "q_1")}, {(1, "q_2")}
    )
    expected = PGA({"q_1", "q_2"}, {"1": [(1, "q_1", "q_2")]}, {(1, "q_1")}, {(1, "q_2")})
    actual = remove_noncoaccessible_states(aut)
    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )


def test_remove_non_coaccessible_states_remove_final_states():
    """Edge case 2: Final states have weight 0"""
    aut = PGA(
        {"q_0", "q_1", "q_2"}, {"1": [(1, "q_0", "q_1"), (1, "q_0", "q_2")]}, {(1, "q_0")}, {(1, "q_1"), (0, "q_2")}
    )
    expected = PGA({"q_0", "q_1"}, {"1": [(1, "q_0", "q_1")]}, {(1, "q_0")}, {(1, "q_1")})
    actual = remove_noncoaccessible_states(aut)
    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )


def test_remove_everything():
    """If everything is removed, the zero-subdistribution PGA should be returned"""
    aut = PGA(
        {"q_0"},
        {},
        {},
        {}
    )
    expected = PGAFactory.zero()
    actual = remove_noncoaccessible_states(aut)
    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )
    
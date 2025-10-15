from symengine import Rational
from automata_inference.automata_factory import PGA, DFAFactory, PGAFactory
from tests.utils import compare_dicts_with_unordered_lists


def test_product_true():
    DFA_true = DFAFactory.neg(DFAFactory.false())
    aut = PGA(
        {"q_0", "q_1", "q_2", "q_3"},
        {
            "X": [(Rational(1, 1), "q_0", "q_1")],
            "Y": [(Rational(1, 1), "q_1", "q_2")],
            "1": [(Rational(1, 1), "q_2", "q_3")],
        },
        {(Rational(1, 1), "q_0")},
        {(Rational(1, 1), "q_3")},
    )
    expected = PGA(
        {"(q_0,p_0)", "(q_1,p_0)", "(q_2,p_0)", "(q_3,p_0)"},
        {
            "X": [(Rational(1, 1), "(q_0,p_0)", "(q_1,p_0)")],
            "Y": [(Rational(1, 1), "(q_1,p_0)", "(q_2,p_0)")],
            "1": [(Rational(1, 1), "(q_2,p_0)", "(q_3,p_0)")],
        },
        {(Rational(1, 1), "(q_0,p_0)")},
        {(Rational(1, 1), "(q_3,p_0)")},
    )  # Nothing is filtered
    actual = aut.product(DFA_true)
    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )


def test_product_false():
    DFA_false = DFAFactory.false()
    aut = PGA(
        {"q_0", "q_1", "q_2", "q_3"},
        {
            "X": [(Rational(1, 1), "q_0", "q_1")],
            "Y": [(Rational(1, 1), "q_1", "q_2")],
            "1": [(Rational(1, 1), "q_2", "q_3")],
        },
        {(Rational(1, 1), "q_0")},
        {(Rational(1, 1), "q_3")},
    )
    expected = PGAFactory.zero()  # Everything is filtered
    actual = aut.product(DFA_false)
    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )


def test_product_filter():
    dfa = DFAFactory.mod("X", 3, 1)
    aut = PGAFactory.geometric("X", Rational(1, 2))
    expected = PGA(
        {"(q_0,p_0)", "(q_0,p_1)", "(q_0,p_2)"},
        {
            "X": [
                (Rational(1, 2), "(q_0,p_0)", "(q_0,p_1)"),
                (Rational(1, 2), "(q_0,p_1)", "(q_0,p_2)"),
                (Rational(1, 2), "(q_0,p_2)", "(q_0,p_0)"),
            ],
            "Y": [],
            "Z": [],
            "1": [],
        },
        {(Rational(1, 1), "(q_0,p_0)")},
        {(Rational(1, 2), "(q_0,p_1)")},
    )
    actual = aut.product(dfa)
    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )

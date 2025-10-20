from automata_inference.automata_factory import PGAFactory, PGA
from automata_inference.program_context import ProgramContext
from symengine import Rational
from tests.utils import compare_dicts_with_unordered_lists

CONSTANT_KEY = "1"


class TestOneSubs:
    """Tests substitution by 1."""

    def test_no_change(self):
        """Nothing changes."""
        context = ProgramContext({"X", "Y", "1"})
        pga = PGAFactory.geometric("Y", Rational(1, 2), context.indeterminates)
        pga_subs = pga.substitute("X", 1, context)
        assert pga == pga_subs  # Nothing should change

    def test_dirac_pga(self):
        """One transition between two states changes."""
        context = ProgramContext({"X", "1"})
        pga = PGAFactory.dirac("X", 1, context.indeterminates)
        actual = pga.substitute("X", 1, context)
        expected = PGA(
            {"q_0", "q_1"},
            {"X": [], "1": [(Rational(1, 1), "q_0", "q_1")]},
            {(Rational(1, 1), "q_0")},
            {(Rational(1, 1), "q_1")},
        )
        assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
        assert expected.initial == actual.initial, (
            f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
        )
        assert expected.final == actual.final, (
            f"Final states do not match, expected {expected.final}, got {actual.final}"
        )
        assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
            f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
        )

    def test_geometric_pga(self):
        """One self-loop changes"""
        context = ProgramContext({"X", "1"})
        pga = PGAFactory.geometric("X", Rational(1, 2), context.indeterminates)
        actual = pga.substitute("X", 1, context)
        expected = PGA(
            {"q_0"},
            {"X": [],  "1": [(Rational(1, 2), "q_0", "q_0")]},
            {(Rational(1, 1), "q_0")},
            {(Rational(1, 2), "q_0")},
        )

        assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
        assert expected.initial == actual.initial, (
            f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
        )
        assert expected.final == actual.final, (
            f"Final states do not match, expected {expected.final}, got {actual.final}"
        )
        assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
            f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
        )


class TestZeroSubs:
    """Tests substitution by 0."""

    def test_no_change(self):
        """Nothing changes"""
        context = ProgramContext({"X", "Y", "1"})
        pga = PGAFactory.geometric("Y", Rational(1, 2), context.indeterminates)
        pga_subs = pga.substitute("X", 0, context)
        assert pga == pga_subs  # Nothing should change

    def test_dirac_pga(self):
        """One transition between two states changes."""
        context = ProgramContext({"X", "1"})
        pga = PGAFactory.dirac("X", 1, context.indeterminates)
        actual = pga.substitute("X", 0, context)
        expected = PGA({"q_0"}, {"X": [], "1": []}, {(Rational(1, 1), "q_0")}, set())
        assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
        assert expected.initial == actual.initial, (
            f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
        )
        assert expected.final == actual.final, (
            f"Final states do not match, expected {expected.final}, got {actual.final}"
        )
        assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
            f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
        )

    def test_geometric_pga(self):
        """One self-loop changes."""
        context = ProgramContext({"X", "1"})
        pga = PGAFactory.geometric("X", Rational(1, 2), context.indeterminates)
        actual = pga.substitute("X", 0, context)
        expected = PGA(
            {"q_0"}, {"X": [], "1": []}, {(Rational(1, 1), "q_0")}, {(Rational(1, 2), "q_0")}
        )

        assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
        assert expected.initial == actual.initial, (
            f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
        )
        assert expected.final == actual.final, (
            f"Final states do not match, expected {expected.final}, got {actual.final}"
        )
        assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
            f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
        )

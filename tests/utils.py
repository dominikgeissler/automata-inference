from symengine import Rational
from collections import Counter

from automata_inference.automata.model import PGA, State, Transition


class AutomatonTestUtils:

    @staticmethod
    def create_pga(
        namespace: int,
        number_of_states: int,
        transitions: list[tuple[int, int, str | None, Rational]],
        initial: list[tuple[Rational, int]],
        final: list[tuple[Rational, int]],
    ) -> PGA:
        return PGA(
            {State(namespace, i) for i in range(number_of_states)},
            {
                Transition(
                    State(namespace, source), State(namespace, target), symbol, weight
                )
                for (source, target, symbol, weight) in transitions
            },
            {(weight, State(namespace, state)) for (weight, state) in initial},
            {(weight, State(namespace, state)) for (weight, state) in final},
        )

    @staticmethod
    def assert_equal_pga(expected: PGA, actual: PGA):
        assert expected.states == actual.states, (
            f"States do not match.\n"
            f"Missing from actual: {expected.states - actual.states}\n"
            f"Extra in actual: {actual.states - expected.states}\n"
            f"Expected state types: {[type(state) for state in expected.states]}\n"
            f"Actual state types: {[type(state) for state in actual.states]}"
        )
        assert expected.initial == actual.initial, (
            f"Initial vector does not match.\n"
            f"Missing from actual: {expected.initial - actual.initial}\n"
            f"Extra in actual: {actual.initial - expected.initial}\n"
            f"Expected initial vector: {expected.initial}\n"
            f"Actual initial vector: {actual.initial}"
        )
        assert expected.final == actual.final, (
            f"Final vector does not match.\n"
            f"Missing from actual: {expected.final - actual.final}\n"
            f"Extra in actual: {actual.final - expected.final}\n"
            f"Expected final vector: {expected.final}\n"
            f"Actual final vector: {actual.final}"
        )
        assert len(expected.transition_matrix) == len(actual.transition_matrix), (
            f"Transition matrices have different numbers of entries.\n"
            f"Expected ({len(expected.transition_matrix)}): {expected.transition_matrix}\n"
            f"Actual ({len(actual.transition_matrix)}): {actual.transition_matrix}"
        )
        expected_transitions = Counter(
            (transition.source, transition.target, transition.weight, transition.symbol)
            for transition in expected.transition_matrix
        )
        actual_transitions = Counter(
            (transition.source, transition.target, transition.weight, transition.symbol)
            for transition in actual.transition_matrix
        )
        assert expected_transitions == actual_transitions, (
            "Transition matrices do not match.\n"
            f"Missing from actual: {expected_transitions - actual_transitions}\n"
            f"Extra in actual: {actual_transitions - expected_transitions}\n"
            f"Expected: {expected.transition_matrix}\n"
            f"Actual: {actual.transition_matrix}"
        )

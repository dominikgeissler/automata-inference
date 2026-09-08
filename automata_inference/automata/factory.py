from __future__ import annotations

from automata_inference.automata.model import (
    DFA,
    PGA,
    ProductState,
    State,
    StateLike,
    Transition,
    new_state_namespace,
)


class PGAFactory:
    """Constructs distribution PGAs."""

    @classmethod
    def zero(cls) -> PGA:
        """Returns the PGA encoding the zero subdistribution.

        Returns:
            PGA: The PGA encoding the zero subdistribution.
        """
        from symengine import Rational

        namespace = new_state_namespace()
        return PGA({State(namespace, 0)}, set(), {(Rational(1, 1), State(namespace, 0))}, set())

    @classmethod
    def one(cls) -> PGA:
        """Returns the PGA encoding the one distribution."""
        from symengine import Rational

        namespace = new_state_namespace()
        return PGA(
            {State(namespace, 0)},
            set(),
            {(Rational(1, 1), State(namespace, 0))},
            {(Rational(1, 1), State(namespace, 0))},
        )

    # --- Distributions ---
    @classmethod
    def geometric(cls, indeterminate: str, p: "Rational") -> PGA:
        """Returns the PGA encoding the geometric distribution for `indeterminate` with parameter `p`."""
        from symengine import Rational

        namespace = new_state_namespace()
        s = State(namespace, 0)
        return PGA(
            {s},
            {Transition(s, s, indeterminate, 1 - p)},
            {(Rational(1, 1), s)},
            {(p, s)},
        )

    @classmethod
    def dirac(cls, indeterminate: str, n: int) -> PGA:
        """Returns the PGA encoding the dirac distribution with parameter `n`."""
        from symengine import Rational

        namespace = new_state_namespace()
        return PGA(
            {State(namespace, i) for i in range(n + 1)},
            {Transition(State(namespace, i), State(namespace, i + 1), indeterminate) for i in range(n)},
            {(Rational(1, 1), State(namespace, 0))},
            {(Rational(1, 1), State(namespace, n))},
        )

    @classmethod
    def uniform(cls, indeterminate: str, n: int) -> PGA:
        """Returns the PGA encoding the uniform distribution with parameter `n`."""
        from symengine import Rational

        namespace = new_state_namespace()
        return PGA(
            {State(namespace, i) for i in range(n)},
            {Transition(State(namespace, i), State(namespace, i + 1), indeterminate) for i in range(n - 1)},
            {(Rational(1, 1), State(namespace, 0))},
            {(Rational(1, n), State(namespace, i)) for i in range(n)},
        )

    @classmethod
    def bernoulli(cls, indeterminate: str, p: "Rational") -> PGA:
        """Returns the PGA encoding the bernoulli distribution with parameter `p`."""
        from symengine import Rational

        namespace = new_state_namespace()
        return PGA(
            {State(namespace, 0), State(namespace, 1)},
            {Transition(State(namespace, 0), State(namespace, 1), indeterminate, p)},
            {(Rational(1, 1), State(namespace, 0))},
            {(1 - p, State(namespace, 0)), (Rational(1, 1), State(namespace, 1))},
        )

    @classmethod
    def neg_binomial(cls, indeterminate: str, n: int, p: "Rational") -> PGA:
        """Returns the PGA encoding the negative binomial distribution."""
        aut = PGAFactory.geometric(indeterminate, p)
        for _ in range(n - 1):
            aut = aut.concat(PGAFactory.geometric(indeterminate, p))
        return aut


# TODO
#   here i actually need all indeterminates to introduce the self-loops
#   i could also handle this in the filter-method


class DFAFactory:
    """Constructs guard DFAs."""

    @classmethod
    def false(cls, indeterminates: set[str]) -> DFA:
        namespace = new_state_namespace()
        s = State(namespace, 0)
        return DFA({s}, _reflexive_closure(indeterminates, {s}), {s}, set())

    @classmethod
    def lt(cls, indeterminate: str, val: int, indeterminates: set[str]) -> DFA:
        namespace = new_state_namespace()
        states: set[StateLike] = {State(namespace, i) for i in range(val + 1)}
        initial: set[StateLike] = {State(namespace, 0)}
        final: set[StateLike] = {State(namespace, i) for i in range(val)}
        transition_matrix = (
            {Transition(State(namespace, i), State(namespace, i + 1), indeterminate) for i in range(val)}
            | {Transition(State(namespace, val), State(namespace, val), indeterminate)}
            | _reflexive_closure(indeterminates - {indeterminate}, states)
        )
        return DFA(states, transition_matrix, initial, final)

    @classmethod
    def mod(
        cls, indeterminate: str, modulus: int, residue: int, indeterminates: set[str]
    ) -> DFA:
        assert modulus > residue, "Modulus has to be greater than residue."
        namespace = new_state_namespace()
        states: set[StateLike] = {State(namespace, i) for i in range(modulus)}
        initial: set[StateLike] = {State(namespace, 0)}
        final: set[StateLike] = {State(namespace, residue)}
        transition_matrix = (
            {Transition(State(namespace, i), State(namespace, i + 1), indeterminate) for i in range(modulus - 1)}
            | {
                Transition(
                    State(namespace, modulus - 1), State(namespace, 0), indeterminate
                )
            }
            | _reflexive_closure(indeterminates - {indeterminate}, states)
        )
        return DFA(states, transition_matrix, initial, final)

    # -------- Syntactic Sugar --------------
    @classmethod
    def eq(cls, indeterminate: str, val: int, indeterminates: set[str]) -> DFA:
        namespace = new_state_namespace()
        states: set[StateLike] = {State(namespace, i) for i in range(val + 2)}
        initial: set[StateLike] = {State(namespace, 0)}
        final: set[StateLike] = {State(namespace, val)}
        transition_matrix: set[Transition] = (
            {Transition(State(namespace, i), State(namespace, i + 1), indeterminate) for i in range(val + 1)}
            | {Transition(State(namespace, val + 1), State(namespace, val + 1), indeterminate)}
            | _reflexive_closure(indeterminates - {indeterminate}, states)
        )
        return DFA(states, transition_matrix, initial, final)

    @classmethod
    def neg(cls, dfa: DFA) -> DFA:
        namespace = new_state_namespace()
        if all(isinstance(state, State) for state in dfa.states):
            state_map = {state: State(namespace, state.index) for state in dfa.states if isinstance(state, State)}
        else:
            state_map = {state: State(namespace, index) for index, state in enumerate(sorted(dfa.states, key=str))}
        return DFA(
            set(state_map.values()),
            {Transition(state_map[t.source], state_map[t.target], t.symbol, t.weight) for t in dfa.transition_matrix},
            {state_map[state] for state in dfa.initial},
            {state_map[state] for state in dfa.states - dfa.final},
        )

    @classmethod
    def land(cls, dfa1: DFA, dfa2: DFA) -> DFA:
        states: set[StateLike] = {ProductState(s1, s2) for s1 in dfa1.states for s2 in dfa2.states}
        initial: set[StateLike] = {ProductState(s1, s2) for s1 in dfa1.initial for s2 in dfa2.initial}
        final: set[StateLike] = {ProductState(s1, s2) for s1 in dfa1.final for s2 in dfa2.final}
        transition_matrix: set[Transition] = set()
        for indeterminate in dfa1.get_symbols().intersection(dfa2.get_symbols()):
            transition_matrix = transition_matrix | {
                Transition(
                    ProductState(t1.source, t2.source),
                    ProductState(t1.target, t2.target),
                    indeterminate,
                )
                for t1 in dfa1.get_transitions_for_symbol(indeterminate)
                for t2 in dfa2.get_transitions_for_symbol(indeterminate)
            }
        return DFA(states, transition_matrix, initial, final)


def _reflexive_closure(indeterminates: set[str], states: set[StateLike]):
    return {Transition(state, state, symbol) for state in states for symbol in indeterminates}

from automata_inference.automata.model import (
    PGA,
    DFA,
    new_state_namespace,
    State,
    Transition,
    ProductState,
    StateLike,
)
from symengine import Rational


class PGAFactory:
    """Constructs distribution PGAs."""

    @classmethod
    def zero(cls) -> PGA:
        """Returns the PGA encoding the zero subdistribution.

        Args:
            indeterminates (set[str]): The set of indeterminates.

        Returns:
            PGA: The PGA encoding the zero subdistribtion.
        """
        namespace = new_state_namespace()
        return PGA(
            {State(namespace, 0)}, set(), {(Rational(1, 1), State(namespace, 0))}, set()
        )

    @classmethod
    def one(cls) -> PGA:
        """Returns the PGA encoding the one distribution.

        Args:
            indeterminates (set[str]): The set of indeterminates.

        Returns:
            PGA: The PGA encoding the one distribution,
        """
        namespace = new_state_namespace()
        return PGA(
            {State(namespace, 0)},
            set(),
            {(Rational(1, 1), State(namespace, 0))},
            {(Rational(1, 1), State(namespace, 0))},
        )

    # --- Distributions ---
    @classmethod
    def geometric(cls, indeterminate: str, p: Rational) -> PGA:
        """Returns the PGA encoding the geometric distribution for indeterminate `indeterminate` with parameter `p`.

        Args:
            indeterminate (str): The indeterminate.
            p (Rational): The parameter (probability).
            indeterminates (set[str]): The set of indeterminates.

        Returns:
            PGA: The PGA encoding the geometric distribution.
        """
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
        """Returns the PGA encoding the dirac disribution with indeterminate `indeterminate` and parameter `n`.

        Args:
            indeterminate (str): The indeterminate.
            n (int): The parameter (natural number).
            indeterminates (set[str]): The set of indeterminates.

        Returns:
            PGA: The PGA encoding the dirac distribution.
        """
        namespace = new_state_namespace()
        return PGA(
            {State(namespace, i) for i in range(n + 1)},
            {
                Transition(State(namespace, i), State(namespace, i + 1), indeterminate)
                for i in range(n)
            },
            {(Rational(1, 1), State(namespace, 0))},
            {(Rational(1, 1), State(namespace, n))},
        )

    @classmethod
    def uniform(cls, indeterminate: str, n: int) -> PGA:
        """Returns the PGA encoding the uniform distribution with indeterminate `indeterminate` and parameter `n`.

        Args:
            indeterminate (str): The indeterminate.
            n (int): The parameter (natural number).
            indeterminates (set[str]): The set of indeterminates.

        Returns:
            PGA: The PGA encoding the uniform distribution.
        """
        namespace = new_state_namespace()
        return PGA(
            {State(namespace, i) for i in range(n)},
            {
                Transition(State(namespace, i), State(namespace, i + 1), indeterminate)
                for i in range(n - 1)
            },
            {(Rational(1, 1), State(namespace, 0))},
            {(Rational(1, n), State(namespace, i)) for i in range(n)},
        )

    @classmethod
    def bernoulli(cls, indeterminate: str, p: Rational) -> PGA:
        """Returns the PGA encoding the bernoulli distribution with indeterminate `indeterminate` and parameter `p`.

        Args:
            indeterminate (str): The indeterminate.
            p (Rational): The parameter (probability).
            indeterminates (set[str]): The set of indeterminates.

        Returns:
            PGA: The PGA encoding the bernoulli distribution.
        """
        namespace = new_state_namespace()
        return PGA(
            {State(namespace, 0), State(namespace, 1)},
            {Transition(State(namespace, 0), State(namespace, 1), indeterminate, p)},
            {(Rational(1, 1), State(namespace, 0))},
            {(1 - p, State(namespace, 0)), (Rational(1, 1), State(namespace, 1))},
        )

    @classmethod
    def neg_binomial(cls, indeterminate: str, n: int, p: Rational) -> PGA:
        """Returns the PGA encoding the negative binomial distribution with indeterminate `indeterminate` and
        parameter `n` and `p`.

        Args:
            indeterminate (str): The indeterminate.
            n (int): The parameter (natural number).
            p (Rational): The parameter (probability).
            indeterminates (set[str]): The set of indeterminates.

        Returns:
            PGA: The PGA encoding the negative binomial distribution.
        """
        aut = PGAFactory.geometric(indeterminate, p)
        for _ in range(n - 1):
            aut = aut.concat(PGAFactory.geometric(indeterminate, p))
        return aut


# FIXME
#   here i actually need all indeterminates to introduce the self-loops
#   i could also handle this in the filter-method


class DFAFactory:
    """Constructs guard DFAs."""

    @classmethod
    def false(cls, indeterminates: set[str]) -> DFA:
        """The DFA encoding the guard `false`.

        Args:
            indeterminates (set[str]): The set of indeterminates.

        Returns:
            DFA: The DFA encoding the guard.
        """
        namespace = new_state_namespace()
        s = State(namespace, 0)
        return DFA({s}, _reflexive_closure(indeterminates, {s}), {s}, set())

    @classmethod
    def lt(cls, indeterminate: str, val: int, indeterminates: set[str]) -> DFA:
        """The DFA encoding the less-than guard `indeterminate` < `val`.

        Args:
            indeterminate (str): The indeterminate.
            val (int): The value its count should be less than.
            indeterminates (set[str]): The set of indeterminates.

        Returns:
            DFA: The DFA encoding the guard.
        """
        namespace = new_state_namespace()
        states = {State(namespace, i) for i in range(val + 1)}
        initial = {State(namespace, 0)}
        final = {State(namespace, i) for i in range(val)}
        transition_matrix = (
            {
                Transition(State(namespace, i), State(namespace, i + 1), indeterminate)
                for i in range(val)
            }
            | {Transition(State(namespace, val), State(namespace, val), indeterminate)}
            | _reflexive_closure(indeterminates - {indeterminate}, states)
        )
        return DFA(states, transition_matrix, initial, final)

    @classmethod
    def mod(
        cls, indeterminate: str, modulus: int, residue: int, indeterminates: set[str]
    ) -> DFA:
        """The DFA encoding the modulus guard `indeterminate` mod `modulus` = `residue`. `modulus` has to be greater
        than `residue`.

        Args:
            indeterminate (str): The indeterminate.
            modulus (int): The modulus.
            residue (int): The residue from the operation.
            indeterminates (set[str]): The set of indeterminates.

        Returns:
            DFA: The DFA encoding the guard.
        """
        assert modulus > residue, "Modulus has to be greater than residue."
        namespace = new_state_namespace()
        states = {State(namespace, i) for i in range(modulus)}
        initial = {State(namespace, 0)}
        final = {State(namespace, residue)}
        transition_matrix = (
            {
                Transition(State(namespace, i), State(namespace, i + 1), indeterminate)
                for i in range(modulus - 1)
            }
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
        """The DFA encoding the equality guard `indeterminate` = `val`.

        Args:
            indeterminate (str): The indeterminate.
            val (int): The number the amount of indeterminates should be equal to.
            indeterminates (set[str]): The set of indeterminates.

        Returns:
            DFA: The DFA encoding the guard.
        """
        # assert val >= 0, f"n has to be greater or equal to 0, got {val=}"
        namespace = new_state_namespace()
        states = {State(namespace, i) for i in range(val + 2)}
        initial = {State(namespace, 0)}
        final = {State(namespace, val)}
        transition_matrix = (
            {
                Transition(State(namespace, i), State(namespace, i + 1), indeterminate)
                for i in range(val + 1)
            }
            | {
                Transition(
                    State(namespace, val + 1), State(namespace, val + 1), indeterminate
                )
            }
            | _reflexive_closure(indeterminates - {indeterminate}, states)
        )
        return DFA(states, transition_matrix, initial, final)

    @classmethod
    def neg(cls, dfa: DFA) -> DFA:
        """The complement of a DFA.

        Args:
            dfa (DFA): The DFA to be complemented.

        Returns:
            DFA: The complement of the DFA.
        """
        return DFA(
            dfa.states, dfa.transition_matrix, dfa.initial, dfa.states - dfa.final
        )

    @classmethod
    def land(cls, dfa1: DFA, dfa2: DFA) -> DFA:
        """Intersection of two DFAs.

        Args:
            dfa1 (DFA): The first DFA.
            dfa2 (DFA): The second DFA:
            indeterminates (set[str]): The set of indeterminates.

        Returns:
            DFA: The resulting intersection DFA.
        """
        states = {
            ProductState(state1, state2)
            for state1 in dfa1.states
            for state2 in dfa2.states
        }
        initial = {
            ProductState(state1, state2)
            for state1 in dfa1.initial
            for state2 in dfa2.initial
        }
        final = {
            ProductState(state1, state2)
            for state1 in dfa1.final
            for state2 in dfa2.final
        }
        transition_matrix = {}
        for indeterminate in dfa1.get_symbols().intersection(dfa2.get_symbols()):
            transition_matrix = transition_matrix | {
                Transition(
                    ProductState(transition1.source, transition2.source),
                    ProductState(transition1.target, transition2.target),
                    indeterminate,
                )
                for transition1 in dfa1.get_transitions_for_symbol(indeterminate)
                for transition2 in dfa2.get_transitions_for_symbol(indeterminate)
            }
        return DFA(states, transition_matrix, initial, final)


def _reflexive_closure(indeterminates: set[str], states: set[StateLike]):
    return {
        Transition(state, state, symbol)
        for state in states
        for symbol in indeterminates
    }

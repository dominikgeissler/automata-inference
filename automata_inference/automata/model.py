from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from fractions import Fraction
from itertools import product

from symengine import Matrix, Rational, eye

# Ensures that automata have disjoint state sets
_namespace_id = -1


@dataclass(frozen=True)
class State:
    """Represents a state in the automaton.

    Args:
        namespace (int): The namespace of the state.
        index (int): The index of the state within its namespace.
    """

    namespace: int
    index: int

    def __str__(self):
        return f"q{self.namespace}_{self.index}"


def new_state_namespace() -> int:
    """Generates a new namespace for states."""
    global _namespace_id
    _namespace_id += 1
    return _namespace_id


def current_state_namespace() -> int:
    """Returns the current namespace. Used for testing."""
    return _namespace_id


@dataclass(frozen=True)
class ProductState:
    left: StateLike
    right: StateLike

    def __str__(self):
        return f"({self.left}, {self.right})"


@dataclass(frozen=True)
class IndexedState:
    state: StateLike
    index: int

    def __str__(self):
        return f"{self.state}_{self.index}"


StateLike = State | ProductState | IndexedState


@dataclass(frozen=True)
class Transition:
    """Models a transition on an automaton.

    Args:
        source (State): The source state of the transition.
        target (State): The target state of the transition.
        symbol (str | None): The symbol associated with the transition (or None, if the transition is constant).
        weight (Rational): The weight (!= 0) of the transition (Defaults to 1).
    """

    source: StateLike
    target: StateLike
    symbol: str | None = None
    weight: Rational = Rational(1, 1)

    def __str__(self):
        return f"{self.source} - {self.weight} " + (f" * {self.symbol} " if self.symbol else "") + f"-> {self.target}"

    def __repr__(self):
        return str(self)


@dataclass
class Automaton(ABC):
    """Represents the abstract notion of an automaton.

    Args:
        states (set[State]): The set of states.
        transition_matrix (set[Transition]): The transition matrix.
        initial (set): The set of initial states.
        final (set): The set of final states.
    """

    states: set[StateLike]
    transition_matrix: set[Transition]
    initial: set
    final: set

    def __str__(self):
        return (
            f"States: {self.states}, Transition matrix: {self.transition_matrix}, "
            + f"Initial: {self.initial}, Final: {self.final}"
        )

    def get_transitions(self, source: StateLike, target: StateLike, symbol: str | None = None) -> set[Transition]:
        """Returns the transitions between two specified states.

        Args:
            source (State): The source state.
            target (State): The target state.
            symbol (str | None, optional): The symbol for which to return transitions (or None, if constant transitions are needed). Defaults to None.

        Returns:
            set[Transition]: The list of transitions between the specified states.
        """
        return {
            transition
            for transition in self.transition_matrix
            if transition.source == source
            and transition.target == target
            and (symbol is None or transition.symbol == symbol)
        }

    def get_transitions_for_symbol(self, symbol: str | None) -> set[Transition]:
        """Returns the transitions for a specified symbol.

        Args:
            symbol (str | None): The symbol for which to return transitions (or None, if constant transitions are needed).

        Returns:
            set[Transition]: The list of transitions for the specified symbol (or constant transitions if symbol is None).
        """
        return {transition for transition in self.transition_matrix if transition.symbol == symbol}

    def get_symbols(self) -> set[str | None]:
        """Returns the set of symbols used within the automaton.

        Returns:
            set[str]: All symbols used on transitions.
        """
        return set(transition.symbol for transition in self.transition_matrix)


@dataclass
class DFA(Automaton):
    """A DFA (deterministic finite automaton). Instantiation of Automaton.

    Args:
        states (set[State]): The set of states.
        transition_matrix (set[Transition]): The transition matrix. (Note: For DFA, the transition matrix is unweighted, so the weight attribute of Transition is not used.)
        initial (set[State]): The set of initial states.
        final (set[State]): The set of final states.
    """

    states: set[StateLike]
    transition_matrix: set[Transition]
    initial: set[StateLike]
    final: set[StateLike]


@dataclass
class PGA(Automaton):
    """A PGA (probability generating automaton). Instantiation of Automaton.

    Args:
        states (set[State]): The set of states.
        transition_matrix (set[Transition]): The transition matrix.
        initial (set[tuple[Rational, State]]): The set of weighted initial states.
        final (set[tuple[Rational, State]]): The set of weighted final states.
    """

    states: set[StateLike]
    transition_matrix: set[Transition]
    initial: set[tuple[Rational, StateLike]]
    final: set[tuple[Rational, StateLike]]

    def concat(self, other: PGA) -> PGA:
        """Concatenates two PGA.

        Args:
            other (PGA): The PGA that should be appended to the end of the current one.

        Returns:
            PGA: The resulting PGA A_1 * A_2.
        """
        new_transition_matrix = (
            self.transition_matrix
            | other.transition_matrix
            | {
                Transition(source, target, weight=c1 * c2)
                for ((c1, source), (c2, target)) in set(product(self.final, other.initial))
            }
        )
        return PGA(self.states | other.states, new_transition_matrix, self.initial, other.final)

    def weighted_union(self, other: PGA, p: Rational, q: Rational) -> PGA:
        """Constructs the disjoint weighted union automaton, given a PGA and two weights p,q.

        Args:
            other (PGA): The other PGA the weighted union should be constructed with,
            p (Rational): The left weight (0 <= p <= 1)
            q (Rational): The right weight (0 <= q <= 1)

        Returns:
            PGA: The resulting PGA A_1 p^+^q A_2.
        """
        # Multiply p and q to the initial weights of A_1 and A_2 respectively
        new_initial = {(p * c, state) for (c, state) in self.initial} | {(q * c, state) for (c, state) in other.initial}
        return PGA(
            self.states | other.states,
            self.transition_matrix | other.transition_matrix,
            new_initial,
            self.final | other.final,
        )

    def substitute(self, indeterminate: str, value: int) -> PGA:
        """Substitutes a given indeterminate by some value in {0,1}.

        Args:
            indeterminate (str): The indeterminate to be substituted
            value (int): The value (0 or 1).

        Returns:
            PGA: The substitution PGA A[X/i].
        """
        # Collect all transitions that need to be changed
        changed_transitions = self.get_transitions_for_symbol(indeterminate)

        # Remove them from the matrix
        new_transition_matrix = self.transition_matrix - changed_transitions

        # If we substitute by 1, we need to add them without symbol
        if value == 1:
            new_transition_matrix = new_transition_matrix | {
                Transition(transition.source, transition.target, weight=transition.weight)
                for transition in changed_transitions
            }
            return PGA(self.states, new_transition_matrix, self.initial, self.final)

        # Since we removed transition, the automaton may have unreachable states
        from automata_inference.automata.operations.minimization import minimize

        return minimize(PGA(self.states, new_transition_matrix, self.initial, self.final))

    def filter(self, other: DFA) -> PGA:
        """Filters the PGA by a given DFA.

        Args:
            other (DFA): The DFA the PGA should by filtered by.
            context (ProgramContext): The program context.

        Returns:
            PGA: The filtered PGA A x B_phi.
        """
        # States are now tuples of states from A and B
        new_states: set[StateLike] = {ProductState(state1, state2) for state1 in self.states for state2 in other.states}

        new_transition_matrix: set[Transition] = set()
        for symbol in self.get_symbols() & other.get_symbols():
            self_transitions = self.get_transitions_for_symbol(symbol)
            other_transitions = other.get_transitions_for_symbol(symbol)
            # Add transitions if the symbols on them coincide (and "multiply" the weights)

            new_transition_matrix.update(
                {
                    Transition(
                        ProductState(transition1.source, transition2.source),
                        ProductState(transition1.target, transition2.target),
                        symbol=symbol,
                        weight=transition1.weight,
                    )
                    for transition1 in self_transitions
                    for transition2 in other_transitions
                }
            )

        # Add "epsilon"-transitions
        new_transition_matrix.update(
            {
                Transition(
                    ProductState(transition.source, q),
                    ProductState(transition.target, q),
                    weight=transition.weight,
                )
                for transition in self.get_transitions_for_symbol(None)
                for q in other.states
            }
        )
        new_initial: set[tuple[Rational, StateLike]] = {(c, ProductState(state1, state2)) for (c, state1) in self.initial for state2 in other.initial}
        new_final: set[tuple[Rational, StateLike]] = {(c, ProductState(state1, state2)) for (c, state1) in self.final for state2 in other.final}
        from automata_inference.automata.operations.minimization import minimize

        return minimize(PGA(new_states, new_transition_matrix, new_initial, new_final))

    def transition_substitution(self, indeterminate, other: PGA) -> PGA:
        """Substitutes all indeterminates of the PGA by the other PGA.

        Args:
            indeterminate (str): The indeterminate to be substituted.
            other (PGA): The PGA that should be inserted for each transition containing the indeterminate.

        Returns:
            PGA: The PGA A_1[X/A_2].
        """
        indet_trans = list(self.get_transitions_for_symbol(indeterminate))  # Order matters here
        new_states = self.states | {IndexedState(state, i) for state in other.states for i in range(len(indet_trans))}

        # All old transitions (with exception of the transitions with the symbol) are part of the new automaton
        new_transition_matrix = {transition for transition in self.transition_matrix if transition not in indet_trans}

        # Connect each A_2 instance
        new_transition_matrix = new_transition_matrix | {
            Transition(
                IndexedState(transition.source, i),
                IndexedState(transition.target, i),
                transition.symbol,
                transition.weight,
            )
            for transition in other.transition_matrix
            for i in range(len(indet_trans))
        }

        for i, transition in enumerate(indet_trans):
            # Add connections to A_2 instances
            new_transition_matrix = new_transition_matrix | {
                Transition(
                    transition.source,
                    IndexedState(state, i),
                    weight=transition.weight * c,
                )
                for (c, state) in other.initial
            }

            # Add connections from A_2 instances back to A_1
            new_transition_matrix = new_transition_matrix | {
                Transition(IndexedState(state, i), transition.target, weight=c) for (c, state) in other.final
            }
        # TODO could return something which needs to be minimized if edge-case distributions are chosen
        return PGA(new_states, new_transition_matrix, self.initial, self.final)

    def decrement(self, indeterminate: str) -> PGA:
        """Creates the decrement automaton for monus.

        Args:
            indeterminate (str): The indeterminate whose value should be decremented.
            context (ProgramContext): The program context.

        Returns:
            PGA: The resulting decrement automaton.
        """
        from automata_inference.automata.factory import DFAFactory

        # Filter the automaton to only contain paths that should be decremented
        guard_dfa = DFAFactory.neg(DFAFactory.lt(indeterminate, 1, {x for x in self.get_symbols() if x is not None}))
        filtered = self.filter(guard_dfa)

        # Paths that do not have any <indeterminate>-transitions
        subs_zero = self.substitute(indeterminate, 0)

        # Remove the first <indeterminate>-transitions
        first_indeterminate_transitions = {
            transition
            for transition in filtered.transition_matrix
            if isinstance(transition.source, ProductState)
            and isinstance(transition.target, ProductState)
            and transition.source.right != transition.target.right
        }

        new_transition_matrix = {
            transition for transition in filtered.transition_matrix if transition not in first_indeterminate_transitions
        }

        # Re-add the transitions, but without symbols
        new_transition_matrix = new_transition_matrix | {
            Transition(transition.source, transition.target, weight=transition.weight)
            for transition in first_indeterminate_transitions
        }

        # Create the updated filtered automaton
        updated_filtered = PGA(filtered.states, new_transition_matrix, filtered.initial, filtered.final)

        # Recombine the updated automaton with the part that only contains paths without any <indeterminate>-transition
        # Simple 'minimization': If subs_zero has no final states it is likely to be the 'zero'-PGA so we can ignore it
        return updated_filtered.weighted_union(subs_zero, 1, 1) if len(subs_zero.final) != 0 else updated_filtered

    def _construct_marginalized_transition_matrix(self, states: list[StateLike]):
        arr = [[Rational(0, 1) for _ in range(len(states))] for _ in range(len(states))]

        for transition in self.transition_matrix:
            pos_source, pos_target = states.index(transition.source), states.index(transition.target)
            arr[pos_source][pos_target] = transition.weight

        return arr

    def _construct_initial_weights_vector(self, states: list[StateLike]) -> list[list[Rational]]:
        arr = [Rational(0, 1)] * len(states)
        for weight, state in self.initial:
            arr[states.index(state)] = weight
        return arr

    def _construct_final_weights_vector(self, states: list[StateLike]) -> list[list[Rational]]:
        arr = [Rational(0, 1)] * len(states)
        for weight, state in self.final:
            arr[states.index(state)] = weight
        return arr

    def get_probability_mass(self) -> Rational:
        """Computes the probability mass symbolically by solving a linear equation system."""
        #
        #   The automaton has to be minimized, otherwise the linear equation system may be infeasible.
        #
        states = list(self.states)
        # Construct the vectors and matrix
        I = Matrix(self._construct_initial_weights_vector(states))
        M = Matrix(self._construct_marginalized_transition_matrix(states))
        F = Matrix(self._construct_final_weights_vector(states))
        A_eq = eye(M.rows) - M
        B = A_eq.LUsolve(F)
        value = I.T @ B
        return Fraction(str(value[0]))

    def normalize(self) -> PGA:
        """Normalizes the PGA by computing the probability mass and weighting the initial weights by its reciprocal.

        Returns:
            PGA: The normalized posterior distribution.
        """
        probability_mass = self.get_probability_mass()
        if probability_mass == 0:
            raise ValueError("Probability mass is equal to 0, normalization undefined")

        normalization_coeff = Rational(probability_mass.denominator, probability_mass.numerator)

        new_initial_weights = {(normalization_coeff * c, q) for (c, q) in self.initial}
        return PGA(self.states, self.transition_matrix, new_initial_weights, self.final)

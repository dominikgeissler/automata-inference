from math import comb

from symengine import Rational

from automata_inference.automata.model import PGA, IndexedState, StateLike, Transition
from automata_inference.automata.operations.minimization import minimize
from automata_inference.parser.ast.queries import (
    MixedMoment,
    PosteriorProbability,
    Query,
    UnivariateMoment,
)
from automata_inference.programs.handlers.guard_handler import GuardHandler


class QueryHandler:
    """Handles the computation of queries."""

    @staticmethod
    def evaluate_query(query: Query, pga: PGA) -> Rational:
        """Evaluates a query on a given PGA.
        
        Args:
            query (Query): The query to evaluate.
            pga (PGA): The PGA on which to evaluate the query.

        Returns:
            Rational: The result of the query evaluation.
        """
        if isinstance(query, PosteriorProbability):
            symbols: set[str] = {x for x in pga.get_symbols() if x is not None}
            guard_handler = GuardHandler(symbols)
            filtered_pga = pga.filter(guard_handler.compile(query.guard))
            return filtered_pga.get_probability_mass()
        if isinstance(query, UnivariateMoment):
            return QueryHandler._evaluate_univariate_moment(query, pga)
        if isinstance(query, MixedMoment):
            return QueryHandler._evaluate_mixed_moment(query, pga)

    @staticmethod
    def _evaluate_univariate_moment(query: UnivariateMoment, pga: PGA) -> Rational:
        # i represents the layer
        new_states: set[StateLike] = {
            IndexedState(q, i) for q in pga.states for i in range(query.moment + 1)
        }

        new_transition_matrix: set[Transition] = set()

        # Connections between layers
        new_transition_matrix.update({
            Transition(
                IndexedState(transition.source, i),
                IndexedState(transition.target, j),
                weight=comb(i, j) * transition.weight,
            )
            for transition in pga.get_transitions_for_symbol(query.variable)
            for i in range(query.moment + 1)
            for j in range(i)
        }
        )

        # Connections within the same layer
        new_transition_matrix.update({
            Transition(
                IndexedState(transition.source, i),
                IndexedState(transition.target, i),
                weight=transition.weight,
            )
            for transition in pga.transition_matrix
            for i in range(query.moment + 1)
        })

        # Initial states are all initial states from the PGA at the top-most layer
        new_initial: set[tuple[Rational, StateLike]] = {
            (weight, IndexedState(state, query.moment))
            for (weight, state) in pga.initial
        }

        # Final states are all final states from the PGA at the bottom-most layer
        new_final: set[tuple[Rational, StateLike]] = {
            (weight, IndexedState(state, 0)) for (weight, state) in pga.final
        }

        # Construct an automaton from it (not rly a PGA though)
        aut = PGA(new_states, new_transition_matrix, new_initial, new_final)

        # Minimize the automaton
        aut = minimize(aut)

        # The probability mass of this automaton is the n-th moment of X in the PGA
        return aut.get_probability_mass()
    
    @staticmethod
    def _evaluate_mixed_moment(query: MixedMoment, pga: PGA) -> Rational:
        # We now have 4 layers
        new_states: set[StateLike] = {IndexedState(q, i) for q in pga.states for i in range(4)}

        new_transition_matrix: set[Transition] = set()

        for transition in pga.transition_matrix:
            # First, we add the connections within the same layer
            new_transition_matrix.update({
                Transition(
                    IndexedState(transition.source, i),
                    IndexedState(transition.target, i),
                    weight=transition.weight,
                )
                for i in range(4)
            })

            # Next, we connect all 'indeterminate1'-transitions from the top-most layer to the 'indeterminate2'-layer
            # W.l.o.g. we say that the 'indeterminate1'-layer is indexed by 1 and 'indeterminate2'-layer is indexed by 2
            if transition.symbol == query.variable1:
                new_transition_matrix.update({
                    Transition(
                        IndexedState(transition.source, 3),
                        IndexedState(transition.target, 2),
                        weight=transition.weight,
                    )
                })

                # Now we connect layer 1 to layer 0
                new_transition_matrix.update({
                    Transition(
                        IndexedState(transition.source, 1),
                        IndexedState(transition.target, 0),
                        weight=transition.weight,
                    )
                })

            # We now do the same thing for 'indeterminate2'
            if transition.symbol == query.variable2:
                new_transition_matrix.update({
                    Transition(
                        IndexedState(transition.source, 3),
                        IndexedState(transition.target, 1),
                        weight=transition.weight,
                    )
                })

                # Now we connect layer 1 and 2 to layer 0
                new_transition_matrix.update({
                    Transition(
                        IndexedState(transition.source, 2),
                        IndexedState(transition.target, 0),
                        weight=transition.weight,
                    )
                })

        # Initial states are all initial states from the PGA on layer 3
        new_initial: set[tuple[Rational, StateLike]] = {
            (weight, IndexedState(state, 3)) for (weight, state) in pga.initial
        }

        # Final states are all final states from the PGA on layer 0
        new_final: set[tuple[Rational, StateLike]] = {
            (weight, IndexedState(state, 0)) for (weight, state) in pga.final
        }

        # Build the automaton (again, not really a PGA)
        aut = PGA(new_states, new_transition_matrix, new_initial, new_final)

        aut = minimize(aut)

        return aut.get_probability_mass()
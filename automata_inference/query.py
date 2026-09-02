from abc import ABC, abstractmethod
from math import comb

from symengine import Rational

from automata_inference.automata_factory import PGA, minimize
from automata_inference.guards import Guard
from automata_inference.program_context import ProgramContext
from automata_inference.visualizer import visualize


def _has_transition(d: dict, x: str | set[str], s: str, t: str) -> Rational:
    """Helper function to return the weight of a transition between two states (if it exists) or 0 otherwise"""
    if isinstance(x, set):
        for v in x:
            values = d[v]
            for a, s1, t1 in values:
                if s == s1 and t == t1:
                    return a
    else:
        values = d[x]
        for a, s1, t1 in values:
            if s == s1 and t == t1:
                return a
    return 0


class Query(ABC):
    """Represents an abstract query.
    """
    @abstractmethod
    def evaluate(self, pga: PGA) -> Rational:
        """Evaluates the query on the given PGA.

        Args:
            pga (PGA): The automaton the query should be evaluated on.
        """


class ProbabilityQuery(Query):
    """Queries the PGA for a posterior probability.
    """
    def __init__(self, guard: Guard):
        self.guard = guard

    def evaluate(self, pga: PGA):
        context = ProgramContext(set(pga.transition_matrix.keys()))
        product = pga.product(self.guard.to_dfa(context), context)

        return minimize(product, set(pga.transition_matrix.keys())).get_probability_mass()


class MomentQuery(Query):
    """Computes the n-th moment of a variable in the PGA.
    """
    def __init__(self, indeterminate: str, moment: int):
        self.indeterminate = indeterminate
        self.moment = moment

    def evaluate(self, pga: PGA):
        pga_states = sorted(pga.states)

        # q represents the index of the state stored in pga_states
        # i represents the layer
        new_states = {f"({q},{i})" for q in range(len(pga_states)) for i in range(self.moment + 1)}

        new_transition_matrix: dict[str, list[tuple[Rational, str, str]]] = {"1": []}

        # Different Layer transitions
        new_transition_matrix["1"].extend(
            [
                (
                    comb(i, j)
                    * _has_transition(pga.transition_matrix, self.indeterminate, pga_states[s], pga_states[t]),
                    f"({s},{i})",
                    f"({t},{j})",
                )
                for s in range(len(pga_states))
                for t in range(len(pga_states))
                for i in range(self.moment + 1)
                for j in range(self.moment + 1)
                if _has_transition(pga.transition_matrix, self.indeterminate, pga_states[s], pga_states[t]) and i > j
            ]
        )

        # Same Layer transitions
        new_transition_matrix["1"].extend(
            (
                _has_transition(pga.transition_matrix, set(pga.transition_matrix.keys()), pga_states[s], pga_states[t]),
                f"({s},{i})",
                f"({t},{i})",
            )
            for s in range(len(pga_states))
            for t in range(len(pga_states))
            for i in range(self.moment + 1)
            if _has_transition(pga.transition_matrix, set(pga.transition_matrix.keys()), pga_states[s], pga_states[t])
        )

        new_initial = {(v, f"({pga_states.index(s)},{self.moment})") for (v, s) in pga.initial if v}

        new_final = {(v, f"({pga_states.index(s)},{0})") for (v, s) in pga.final if v}

        aut = PGA(new_states, new_transition_matrix, new_initial, new_final)  # not rly a PGA though

        aut = minimize(aut, {"1"})

        return aut.get_probability_mass()


class MixedMomentQuery(Query):
    """Computes the mixed moment of two variables in the PGA."""
    def __init__(self, indeterminate1: str, indeterminate2: str):
        self.indeterminate1 = indeterminate1
        self.indeterminate2 = indeterminate2

    def evaluate(self, pga: PGA):
        pga_states = sorted(pga.states)
        new_states = {f"({q},{i})" for q in range(len(pga_states)) for i in range(4)}

        new_transition_matrix: dict[str, list[tuple[Rational, str, str]]] = {"1": []}

        for i in range(4):
            for j in range(4):
                for s in pga_states:
                    for t in pga_states:
                        if (
                            (
                                i == j
                                and _has_transition(
                                    pga.transition_matrix,
                                    set(pga.transition_matrix.keys()),
                                    s,
                                    t,
                                )
                            )
                            or (
                                i == 1
                                and j == 0
                                and _has_transition(
                                    pga.transition_matrix, self.indeterminate1, s, t
                                )
                                != 0
                            )
                            or (
                                i == 2
                                and j == 0
                                and _has_transition(
                                    pga.transition_matrix, self.indeterminate2, s, t
                                )
                                != 0
                            )
                            or (
                                i == 3
                                and j == 1
                                and _has_transition(
                                    pga.transition_matrix, self.indeterminate2, s, t
                                )
                                != 0
                            )
                            or (
                                i == 3
                                and j == 2
                                and _has_transition(
                                    pga.transition_matrix, self.indeterminate1, s, t
                                )
                                != 0
                            )
                        ):
                            new_transition_matrix["1"].append(
                                (
                                    _has_transition(
                                        pga.transition_matrix,
                                        set(pga.transition_matrix.keys()),
                                        s,
                                        t,
                                    ),
                                    f"({pga_states.index(s)},{i})",
                                    f"({pga_states.index(t)},{j})",
                                )
                            )

        new_initial = {(v, f"({pga_states.index(s)},{3})") for (v, s) in pga.initial if v}

        new_final = {(v, f"({pga_states.index(s)},{0})") for (v, s) in pga.final if v}

        aut = PGA(new_states, new_transition_matrix, new_initial, new_final)

        aut = minimize(aut, {"1"})

        return aut.get_probability_mass()

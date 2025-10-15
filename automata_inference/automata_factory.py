from __future__ import annotations

import itertools
from abc import ABC, abstractmethod
from typing import TypeVar

from symengine import Rational

CONSTANT_KEY = "1"
VARIABLES = {"X", "Y", "Z", CONSTANT_KEY}


class Automaton(ABC):
    """Represents the abstract notion of an automaton."""

    @abstractmethod
    def __init__(
        self,
        states: set[str],
        transition_matrix: dict[str, list[tuple]],
        initial: set,
        final: set,
    ):
        self.states = states
        self.transition_matrix = transition_matrix
        self.initial = initial
        self.final = final

    def __str__(self):
        return (
            f"States: {self.states}, Transition matrix: {self.transition_matrix}, "
            + f"Initial: {self.initial}, Final: {self.final}"
        )

    def __eq__(self, value):
        if not isinstance(value, Automaton):
            return False
        return (
            self.states == value.states
            and self.transition_matrix == value.transition_matrix
            and self.initial == value.initial
            and self.final == value.final
        )


# Used for generic function typing
T = TypeVar("T", bound=Automaton)


class DFA(Automaton):
    """
    A DFA (deterministic finite automaton). Instantiation of Automaton.
    """

    def __init__(
        self,
        states: set[str],
        transition_matrix: dict[str, list[tuple[str, str]]],
        initial: set[str],
        final: set[str],
    ):
        self.states = states
        self.transition_matrix = transition_matrix
        self.initial = initial
        self.final = final


class PGA(Automaton):
    """A PGA (probability generating automaton). Instantiation of Automaton."""

    def __init__(
        self,
        states: set[str],
        transition_matrix: dict[str, list[tuple[Rational, str, str]]],
        initial: set[tuple[Rational, str]],
        final: set[tuple[Rational, str]],
    ):
        self.states = states
        self.transition_matrix = transition_matrix
        self.initial = initial
        self.final = final

    def get_probability_mass(self) -> Rational:
        """Calculates the probability mass of the PGA.

        Returns:
            Rational: The probability mass of the PGA.
        """
        raise NotImplementedError("todo")

    def substitute(self, indeterminate: str, value: int) -> PGA:
        """Substitutes a given indeterminate by some value in {0,1}

        Args:
            indeterminate (str): The indeterminate to be substituted
            value (int): The value (0 or 1).

        Returns:
            PGA: The substitution PGA A[X/i].
        """
        assert value in {0, 1}, f"Substitution is only supported for 0 or 1, got {value}"
        new_transition_matrix = self.transition_matrix.copy()
        new_transition_matrix[indeterminate] = []
        new_transition_matrix[CONSTANT_KEY].extend(self.transition_matrix[indeterminate] if value == 1 else [])
        if value == 1:
            return PGA(self.states, new_transition_matrix, self.initial, self.final)
        return minimize(PGA(self.states, new_transition_matrix, self.initial, self.final))

    def concat(self, other: PGA) -> PGA:
        """Concatenates two PGA.

        Args:
            other (PGA): The PGA that should be appended to the end of the current one.

        Returns:
            PGA: The resulting PGA A_1 * A_2.
        """
        other = resolve_conflict(self, other)
        new_transition_matrix = {}
        for k in self.transition_matrix.keys() | other.transition_matrix.keys():
            new_transition_matrix[k] = self.transition_matrix[k] + other.transition_matrix[k]
        if CONSTANT_KEY in new_transition_matrix:
            new_transition_matrix[CONSTANT_KEY] += [
                (c1 * c2, from_state, to_state)
                for ((c1, from_state), (c2, to_state)) in set(itertools.product(self.final, other.initial))
            ]
        else:
            new_transition_matrix[CONSTANT_KEY] = [
                (c1 * c2, from_state, to_state)
                for ((c1, from_state), (c2, to_state)) in set(itertools.product(self.final, other.initial))
            ]
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
        assert 0 <= p <= 1 and 0 <= q <= 1, f"p and q have to be between 0 and 1 , got {p=} and {q=}"
        other = resolve_conflict(self, other)
        new_initial = {(p * c, state) for (c, state) in self.initial} | {(q * c, state) for (c, state) in other.initial}
        print(new_initial)
        new_transition_matrix = {}
        for k in self.transition_matrix.keys() | other.transition_matrix.keys():
            new_transition_matrix[k] = (self.transition_matrix[k] if k in self.transition_matrix else []) + (
                other.transition_matrix[k] if k in other.transition_matrix else []
            )
        return PGA(
            self.states | other.states,
            new_transition_matrix,
            new_initial,
            self.final | other.final,
        )

    def product(self, other: DFA) -> PGA:
        """Filters the PGA by a given DFA.

        Args:
            other (DFA): The DFA the PGA should by filtered by.

        Returns:
            PGA: The filtered PGA A x B_phi.
        """
        # TODO pga and dfa should never have conflict ig
        new_states = {f"({q1},{q2})" for q1 in self.states for q2 in other.states}
        new_transition_matrix = {}
        for v in self.transition_matrix.keys():
            s_trans = self.transition_matrix[v]
            o_trans = other.transition_matrix[v]
            new_transition_matrix[v] = [
                (c, f"({state1},{state2})", f"({state3},{state4})")
                for (c, state1, state3) in s_trans
                for (state2, state4) in o_trans
            ]
        new_initial = set((c, f"({state1},{state2})") for (c, state1) in self.initial for state2 in other.initial)
        new_final = set((c, f"({state1},{state2})") for (c, state1) in self.final for state2 in other.final)
        return minimize(PGA(new_states, new_transition_matrix, new_initial, new_final))

    def transition_substitution(self, indeterminate, other: PGA) -> PGA:
        """Substitutes all indeterminates of the PGA by the other PGA.

        Args:
            indeterminate (str): The indeterminate to be substituted.
            other (PGA): The PGA that should be inserted for each transition containing the indeterminate.

        Returns:
            PGA: The PGA A_1[Y/A_2].
        """
        # FIXME this somehow overwrites self...
        indet_trans = self.transition_matrix[indeterminate]
        other = resolve_conflict(self, other)
        new_states = {f"{q}_{i}" for q in other.states for i in range(len(indet_trans))}

        new_transition_matrix = self.transition_matrix.copy()
        new_transition_matrix[indeterminate] = []

        for v in other.transition_matrix.keys():
            if other.transition_matrix[v]:
                new_transition_matrix[v] += [
                    (c, f"{state1}_{i}", f"{state2}_{i}")
                    for i in range(len(indet_trans))
                    for (c, state1, state2) in other.transition_matrix[v]
                ]
        new_transition_matrix[CONSTANT_KEY].extend(
            [
                (indet_trans[i][0] * c, indet_trans[i][1], f"{q}_{i}")
                for i in range(len(indet_trans))
                for c, q in other.initial
            ]
            + [(c, f"{q}_{i}", indet_trans[i][2]) for c, q in other.final for i in range(len(indet_trans))]
        )
        return PGA(self.states | new_states, new_transition_matrix, self.initial, self.final)

    def decrement(self, indeterminate: str) -> PGA:
        """Creates the decrement automaton for monus.

        Args:
            indeterminate (str): The indeterminate whose value should be decremented.

        Returns:
            PGA: The resulting decrement automaton.
        """

        dfa_filter = DFAFactory.neg(DFAFactory.lt("X", 1))  # TODO dfa and pga should never have conflict ig
        filtered = self.product(dfa_filter)
        subs_zero = self.substitute("X", 0)
        dfa_s, dfa_t = [el for el in dfa_filter.transition_matrix[indeterminate] if el[0] != el[1]][0]
        new_transition_matrix: dict[str, list[tuple[Rational, str, str]]] = filtered.transition_matrix.copy()
        for w, s, t in new_transition_matrix[indeterminate][:]:
            last_state_s, last_state_t = (
                s.split(",")[-1].split(")")[0],
                t.split(",")[-1].split(")")[0],
            )
            if last_state_s == dfa_s and last_state_t == dfa_t:
                new_transition_matrix[indeterminate].remove((w, s, t))
                new_transition_matrix[CONSTANT_KEY].append((w, s, t))
        return minimize(filtered.weighted_union(subs_zero, 1, 1))


def resolve_conflict(a1: Automaton, a2: T) -> T:
    """Checks for disjoint state sets and, if not disjoint, renames the states of the second automaton for the state
    sets to be disjoint. (Also changes the transition matrix and initial / final state sets).

    Args:
        a1 (Automaton): The first automaton.
        a2 (Automaton): The second automaton. This one will be changed.

    Raises:
        ValueError: Invalid transition matrix.

    Returns:
        Automaton: The changed a2 automaton with new state labels that are now disjoint from a1.
    """
    if a1.states.isdisjoint(a2.states):
        return a2
    suffix = "_1"
    while any((s + suffix) in a1.states for s in a2.states):
        suffix += "_"

    rename_map = {s: s + suffix for s in a2.states}

    def rename_set(some_set: set[str]) -> set[str]:
        """Renames a set by some map.

        Args:
            some_set (set[str]): The set to be renamed.

        Returns:
            set[str]: The renamed set.
        """
        return {rename_map.get(s, s) for s in some_set}

    def rename_weighted_set(some_set: set[tuple[Rational, str]]) -> set[tuple[Rational, str]]:
        """Renames a weighted set by some map.

        Args:
            some_set (set[str]): The set to be renamed.

        Returns:
            set[tuple[Rational, str]]: The renamed set.
        """
        return {(w, rename_map.get(s, s)) for w, s in some_set}

    new_transition_matrix_weighted = {}
    new_transition_matrix_unweighted = {}
    for indeterminate, transitions in a2.transition_matrix.items():
        new_entries_weighted: list[tuple[Rational, str, str]] = []
        new_entries_unweighted: list[tuple[str, str]] = []
        for entry in transitions:
            if len(entry) == 2:
                # Unweighted case
                s, t = entry
                new_entries_unweighted.append((rename_map.get(s, s), rename_map.get(t, t)))
            elif len(entry) == 3:
                weight, s, t = entry
                new_entries_weighted.append((weight, rename_map.get(s, s), rename_map.get(t, t)))
            else:
                raise ValueError(f"Weird transition matrix entry {entry}")
        if isinstance(a2, PGA):
            new_transition_matrix_weighted[indeterminate] = new_entries_weighted
        else:
            new_transition_matrix_unweighted[indeterminate] = new_entries_unweighted
    if isinstance(a2, PGA):
        return PGA(
            states=rename_set(a2.states),
            transition_matrix=new_transition_matrix_weighted,
            initial=rename_weighted_set(a2.initial),
            final=rename_weighted_set(a2.final),
        )  # type: ignore[return-value]
    return DFA(
        states=rename_set(a2.states),
        transition_matrix=new_transition_matrix_unweighted,
        initial=rename_set(a2.initial),
        final=rename_set(a2.final),
    )  # type: ignore[return-value]


def minimize(aut: T) -> T:
    """Minimizes the given automaton by removing non-coaccessible states and merging redundant states.

    Args:
        aut (Automaton): The automaton to be minimized.

    Returns:
        Automaton: The minimized automaton.
    """
    aut = remove_noncoaccessible_states(aut)
    # if isinstance(aut, PGA):
    #     aut = merge_states(aut)
    return aut


def remove_noncoaccessible_states(aut: T) -> T:
    """Removes unreachable and non-coaccessible states.

    Args:
        aut (Automaton): The automaton to be minimized

    Returns:
        Automaton: The automaton without unreachable / non-coaccessible states.
    """
    # FIXME this breaks sometimes
    is_pga = isinstance(aut, PGA) or any(isinstance(el, tuple) for el in aut.initial | aut.final)

    # Remove zero initial / final weights
    aut.initial = {el for el in aut.initial if el[0] != 0}
    aut.final = {el for el in aut.final if el[0] != 0}

    def get_state(possible_weighted_state):
        return possible_weighted_state[1] if isinstance(possible_weighted_state, tuple) else possible_weighted_state

    successors: dict[str, set[str]] = {q: set() for q in aut.states}
    predecessors: dict[str, set[str]] = {q: set() for q in aut.states}
    for _, transitions in aut.transition_matrix.items():
        for trans in transitions:
            if is_pga:
                _, s, t = trans
            else:
                s, t = trans
            successors[s].add(t)
            predecessors[t].add(s)

    reachable = set()
    stack = list(get_state(el) for el in aut.initial)

    while stack:
        curr = stack.pop()
        if curr not in reachable:
            reachable.add(curr)
            stack.extend(successors[curr])

    coaccessible = set()
    stack = list(get_state(el) for el in aut.final)

    while stack:
        curr = stack.pop()
        if curr not in coaccessible:
            coaccessible.add(curr)
            stack.extend(predecessors[curr])

    keep = reachable & coaccessible
    if not keep:
        return PGAFactory.zero() if is_pga else DFAFactory.false()  # type: ignore[return-value]

    new_transition_matrix = {}
    aut.states = keep
    for indeterminate, transitions in aut.transition_matrix.items():
        keep_trans_weighted: list[tuple[Rational, str, str]] = []
        keep_trans_unweighted: list[tuple[str, str]] = []
        for trans in transitions:
            if is_pga:
                w, s, t = trans
                if s in keep and t in keep:
                    keep_trans_weighted.append((w, s, t))
            else:
                s, t = trans
                if s in keep and t in keep:
                    keep_trans_unweighted.append((s, t))
        new_transition_matrix[indeterminate] = keep_trans_weighted if is_pga else keep_trans_unweighted
    aut.transition_matrix = new_transition_matrix

    if is_pga:
        aut.initial = {(w, s) for (w, s) in aut.initial if s in keep}
        aut.final = {(w, s) for (w, s) in aut.final if s in keep}
    else:
        aut.initial = aut.initial & keep
        aut.final = aut.final & keep
    return aut


def merge_states(aut: PGA) -> PGA:
    """Minimizes the automaton by merging states.

    Args:
        aut (PGA): The PGA to be minimized.

    Returns:
        PGA: The resulting minimized PGA.
    """
    return aut


# -- Factory --


class PGAFactory:
    """Constructs distribution PGAs."""

    @classmethod
    def zero(cls) -> PGA:
        """Returns the PGA encoding the zero subdistribution.

        Returns:
            PGA: The PGA encoding the zero subdistribtion.
        """
        return PGA({"q_0"}, {v: [] for v in VARIABLES}, {(Rational(1, 1), "q_0")}, set())

    @classmethod
    def one(cls) -> PGA:
        """Returns the PGA encoding the one distribution.

        Returns:
            PGA: The PGA encoding the one distribution,
        """
        return PGA({"q_0"}, {v: [] for v in VARIABLES}, {(Rational(1, 1), "q_0")}, {(Rational(1, 1), "q_0")})

    # --- Distributions ---
    @classmethod
    def geometric(cls, indeterminate: str, p: Rational) -> PGA:
        """Returns the PGA encoding the geometric distribution for indeterminate `indeterminate` with parameter `p`.

        Args:
            indeterminate (str): The indeterminate.
            p (Rational): The parameter (probability).

        Returns:
            PGA: The PGA encoding the geometric distribution.
        """
        return PGA(
            {"q_0"},
            {indeterminate: [(1 - p, "q_0", "q_0")]} | {v: [] for v in VARIABLES - {indeterminate}},
            {(Rational(1, 1), "q_0")},
            {(p, "q_0")},
        )

    @classmethod
    def dirac(cls, indeterminate: str, n: int) -> PGA:
        """Returns the PGA encoding the dirac disribution with indeterminate `indeterminate` and parameter `n`.

        Args:
            indeterminate (str): The indeterminate.
            n (int): The parameter (natural number).

        Returns:
            PGA: The PGA encoding the dirac distribution.
        """
        return PGA(
            {f"q_{i}" for i in range(n + 1)},
            {indeterminate: [(Rational(1, 1), f"q_{i}", f"q_{i + 1}") for i in range(n)]}
            | {v: [] for v in VARIABLES - {indeterminate}},
            {(Rational(1, 1), "q_0")},
            {(Rational(1, 1), f"q_{n}")},
        )

    @classmethod
    def uniform(cls, indeterminate: str, n: int) -> PGA:
        """Returns the PGA encoding the uniform distribution with indeterminate `indeterminate` and parameter `n`.

        Args:
            indeterminate (str): The indeterminate.
            n (int): The parameter (natural number).

        Returns:
            PGA: The PGA encoding the uniform distribution.
        """
        return PGA(
            {f"q_{i}" for i in range(n)},
            {indeterminate: [(Rational(1, 1), f"q_{i}", f"q_{i + 1}") for i in range(n - 1)]}
            | {v: [] for v in VARIABLES - {indeterminate}},
            {(Rational(1, 1), "q_0")},
            {(Rational(1, n), f"q_{i}") for i in range(n)},
        )

    @classmethod
    def bernoulli(cls, indeterminate: str, p: Rational) -> PGA:
        """Returns the PGA encoding the bernoulli distribution with indeterminate `indeterminate` and parameter `p`.

        Args:
            indeterminate (str): The indeterminate.
            p (Rational): The parameter (probability).

        Returns:
            PGA: The PGA encoding the bernoulli distribution.
        """
        return PGA(
            {"q_0", "q_1"},
            {indeterminate: [(p, "q_0", "q_1")]} | {v: [] for v in VARIABLES - {indeterminate}},
            {(Rational(1, 1), "q_0")},
            {(1 - p, "q_0"), (Rational(1, 1), "q_1")},
        )

    @classmethod
    def neg_binomial(cls, indeterminate: str, n: int, p: Rational) -> PGA:
        """Returns the PGA encoding the negative binomial distribution with indeterminate `indeterminate` and
        parameter `n` and `p`.

        Args:
            indeterminate (str): The indeterminate.
            n (int): The parameter (natural number).
            p (Rational): The parameter (probability).

        Returns:
            PGA: The PGA encoding the negative binomial distribution.
        """
        assert n > 0, f"n has to be greater than 0, got {n=}"
        assert 0 <= p <= 1, f"p has to be between 0 and 1, got {p=}"

        aut = PGAFactory.geometric(indeterminate, p)
        for _ in range(n - 1):
            aut = aut.concat(PGAFactory.geometric(indeterminate, p))

        return aut


class DFAFactory:
    """Constructs guard DFAs."""

    @classmethod
    def false(cls) -> DFA:
        """The DFA encoding the guard `false`.

        Returns:
            DFA: The DFA encoding the guard.
        """
        return DFA({"p_0"}, reflexive_closure({}, VARIABLES, {"p_0"}), {"p_0"}, set())

    @classmethod
    def lt(cls, indeterminate: str, val: int) -> DFA:
        """The DFA encoding the less-than guard `indeterminate` < `val`.

        Args:
            indeterminate (str): The indeterminate.
            val (int): The value its count should be less than.

        Returns:
            DFA: The DFA encoding the guard.
        """
        assert val >= 0, "..."
        states = {f"p_{i}" for i in range(val + 1)}
        initial = {"p_0"}
        final = {f"p_{i}" for i in range(val)}
        transition_matrix: dict[str, list[tuple[str, str]]] = {v: [] for v in VARIABLES}
        transition_matrix[indeterminate] = [(f"p_{i}", f"p_{i + 1}") for i in range(val)] + [(f"p_{val}", f"p_{val}")]
        transition_matrix = reflexive_closure(transition_matrix, VARIABLES - {indeterminate}, states)
        return DFA(states, transition_matrix, initial, final)

    @classmethod
    def mod(cls, indeterminate: str, modulus: int, residue: int) -> DFA:
        """The DFA encoding the modulus guard `indeterminate` mod `modulus` = `residue`. `modulus` has to be greater
        than `residue`.

        Args:
            indeterminate (str): The indeterminate.
            modulus (int): The modulus.
            residue (int): The residue from the operation.

        Returns:
            DFA: The DFA encoding the guard.
        """
        assert modulus > residue, "Modulus has to be greater than residue."
        states = {f"p_{i}" for i in range(modulus)}
        initial = {"p_0"}
        final = {f"p_{residue}"}
        transition_matrix: dict[str, list[tuple[str, str]]] = {v: [] for v in VARIABLES}
        transition_matrix[indeterminate] = [(f"p_{i}", f"p_{i + 1}") for i in range(modulus - 1)] + [
            (f"p_{modulus - 1}", "p_0")
        ]
        transition_matrix = reflexive_closure(transition_matrix, VARIABLES - {indeterminate}, states)
        return DFA(states, transition_matrix, initial, final)

    # -------- Syntactic Sugar --------------
    @classmethod
    def eq(cls, indeterminate: str, val: int) -> DFA:
        """The DFA encoding the equality guard `indeterminate` = `val`.

        Args:
            indeterminate (str): The indeterminate.
            val (int): The number the amount of indeterminates should be equal to.

        Returns:
            DFA: The DFA encoding the guard.
        """
        assert val >= 0, f"n has to be greater or equal to 0, got {val=}"
        states = {f"p_{i}" for i in range(val + 2)}
        initial = {"p_0"}
        final = {f"p_{val}"}
        transition_matrix: dict[str, list[tuple[str, str]]] = {v: [] for v in VARIABLES}
        transition_matrix[indeterminate] = [(f"p_{i}", f"p_{i + 1}") for i in range(val + 1)] + [
            (f"p_{val + 1}", f"p_{val + 1}")
        ]
        transition_matrix = reflexive_closure(transition_matrix, VARIABLES - {indeterminate}, states)
        return DFA(states, transition_matrix, initial, final)

    @classmethod
    def neg(cls, dfa: DFA) -> DFA:
        """The complement of a DFA.

        Args:
            dfa (DFA): The DFA to be complemented.

        Returns:
            DFA: The complement of the DFA.
        """
        return DFA(dfa.states, dfa.transition_matrix, dfa.initial, dfa.states - dfa.final)

    @classmethod
    def land(cls, dfa1: DFA, dfa2: DFA) -> DFA:
        """Intersection of two DFAs.

        Args:
            dfa1 (DFA): The first DFA._
            dfa2 (DFA): The second DFA:

        Returns:
            DFA: The resulting intersection DFA.
        """
        states = {f"({state1},{state2})" for state1 in dfa1.states for state2 in dfa2.states}
        initial = {f"({state1},{state2})" for state1 in dfa1.initial for state2 in dfa2.initial}
        final = {f"({state1},{state2})" for state1 in dfa1.final for state2 in dfa2.final}
        transition_matrix = {}
        for v in VARIABLES:
            transition_matrix[v] = [
                (f"({state1},{state2})", f"({state3},{state4})")
                for (state1, state3) in dfa1.transition_matrix[v]
                for (state2, state4) in dfa2.transition_matrix[v]
            ]
        return DFA(states, transition_matrix, initial, final)


# ------- Helpers -------------


def reflexive_closure(
    transition_matrix: dict[str, list[tuple[str, str]]], variables: set[str], states: set[str]
) -> dict[str, list[tuple[str, str]]]:
    """Adds self-loops to every state with the provided variables.

    Args:
        transition_matrix (dict[str, tuple]): The transition matrix to be extended.
        variables (set[str]): The set of variables for which self-loops should be added.
        states (set[str]): The set of states which should have these self-loops.

    Returns:
        dict[str, tuple]: The extended transition matrix.
    """
    for v in variables:
        if not v in transition_matrix:
            transition_matrix[v] = []
        transition_matrix[v] += [(q, q) for q in states]
    return transition_matrix

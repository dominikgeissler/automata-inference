import itertools
from abc import ABC

VARIABLES = {"X", "Y", "Z", 1}

# TODO Remove hardcoded names
# TODO checks that indeterminate is different from 1?
# TODO better way of storing indeterminates / states?

CONSTANT_KEY = 1


class Automaton(ABC):
    """Represents the abstract notion of an automaton."""

    def __init__(
        self, states: set[str], transition_matrix: dict[tuple], initial: set, final: set
    ):
        self.states = states
        self.transition_matrix = transition_matrix
        self.initial = initial
        self.final = final

    def __str__(self):
        return f"States: {self.states}, Transition matrix: {self.transition_matrix}, Initial: {self.initial}, Final: {self.final}"


class DFA(Automaton):
    """
    A DFA (deterministic finite automaton). Instantiation of Automaton.
    """

    def __init__(
        self,
        states,
        transition_matrix: dict[str, list[tuple[str, str]]],
        initial: set[str],
        final: set[str],
    ):
        super().__init__(states, transition_matrix, initial, final)


class PGA(Automaton):
    def __init__(
        self,
        states,
        transition_matrix: dict[str, list[tuple[float, str, str]]],
        initial: set[tuple[float, str]],
        final: set[tuple[float, str]],
    ):
        return super().__init__(states, transition_matrix, initial, final)

    def substitute(self, indeterminate, value: int) -> "PGA":
        """Substitutes a given indeterminate by some value in {0,1}

        Args:
            indeterminate (str): The indeterminate to be substituted
            value (int): The value (0 or 1).

        Returns:
            PGA: The substitution PGA A[X/i].
        """
        assert value in {0, 1}, (
            f"Substitution is only supported for 0 or 1, got {value}"
        )
        new_transition_matrix = self.transition_matrix
        new_transition_matrix[indeterminate] = []
        new_transition_matrix[CONSTANT_KEY].extend(
            self.transition_matrix[indeterminate] if indeterminate == 1 else []
        )
        return PGA(self.states, new_transition_matrix, self.initial, self.final)

    def concat(self, other: "PGA") -> "PGA":
        """Concatenates two PGA.

        Args:
            other (PGA): The PGA that should be appended to the end of the current one.

        Returns:
            PGA: The resulting PGA A_1 * A_2.
        """
        if not self.states.isdisjoint(other.states):
            other = resolve_conflict(self, other)
        new_transition_matrix = dict()
        for k in self.transition_matrix.keys() | other.transition_matrix.keys():
            new_transition_matrix[k] = (
                self.transition_matrix[k] + other.transition_matrix[k]
            )
        if CONSTANT_KEY in new_transition_matrix:
            new_transition_matrix[CONSTANT_KEY] += [
                (c1 * c2, from_state, to_state)
                for ((c1, from_state), (c2, to_state)) in set(
                    itertools.product(self.final, other.initial)
                )
            ]
        else:
            new_transition_matrix[CONSTANT_KEY] = [
                (c1 * c2, from_state, to_state)
                for ((c1, from_state), (c2, to_state)) in set(
                    itertools.product(self.final, other.initial)
                )
            ]
        return PGA(
            self.states | other.states, new_transition_matrix, self.initial, other.final
        )

    def weighted_union(self, other: "PGA", p: float, q: float) -> "PGA":
        """Constructs the disjoint weighted union automaton, given a PGA and two weights p,q.

        Args:
            other (PGA): The other PGA the weighted union should be constructed with,
            p (float): The left weight (0 <= p <= 1)
            q (float): The right weight (0 <= q <= 1)

        Returns:
            PGA: The resulting PGA A_1 p^+^q A_2.
        """
        assert 0 <= p and p <= 1 and 0 <= q and q <= 1, (
            f"p and q have to be between 0 and 1 , got {p=} and {q=}"
        )
        if not self.states.isdisjoint(other.states):
            other = resolve_conflict(self, other)
        new_initial = {(p * c, state) for (c, state) in self.initial} | {
            (q * c, state) for (c, state) in other.initial
        }
        new_transition_matrix = dict()
        for k in self.transition_matrix.keys() | other.transition_matrix.keys():
            new_transition_matrix[k] = (
                self.transition_matrix[k] if k in self.transition_matrix else []
            ) + (other.transition_matrix[k] if k in other.transition_matrix else [])
        return PGA(
            self.states | other.states,
            new_transition_matrix,
            new_initial,
            self.final | other.final,
        )

    def product(self, other: DFA) -> "PGA":
        """Filters the PGA by a given DFA.

        Args:
            other (DFA): The DFA the PGA should by filtered by.

        Returns:
            PGA: The filtered PGA A x B_phi.
        """
        if not self.states.isdisjoint(other.states):
            other = resolve_conflict(self, other)
        new_states = {f"({q1},{q2})" for q1 in self.states for q2 in other.states}
        new_transition_matrix = dict()
        for v in self.transition_matrix.keys():
            s_trans = self.transition_matrix[v]
            o_trans = other.transition_matrix[v]
            new_transition_matrix[v] = [
                (c, f"({state1},{state2})", f"({state3},{state4})")
                for (c, state1, state3) in s_trans
                for (state2, state4) in o_trans
            ]
        new_initial = set(
            (c, f"({state1},{state2})")
            for (c, state1) in self.initial
            for state2 in other.initial
        )
        new_final = set(
            (c, f"({state1},{state2})")
            for (c, state1) in self.final
            for state2 in other.final
        )

        return PGA(new_states, new_transition_matrix, new_initial, new_final)

    def transition_substitution(self, indeterminate, other: "PGA") -> "PGA":
        """Substitutes all indeterminates of the PGA by the other PGA.

        Args:
            indeterminate (str): The indeterminate to be substituted.
            other (PGA): The PGA that should be inserted for each transition containing the indeterminate.

        Returns:
            PGA: The PGA A_1[Y/A_2].
        """
        indet_trans = self.transition_matrix[indeterminate]
        new_states = set(
            [f"{q}_{i}" for q in other.states for i in range(len(indet_trans))]
        )
        if not self.states.isdisjoint(other.states):
            other = resolve_conflict(self, other)

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
            + [
                (c, f"{q}_{i}", indet_trans[i][2])
                for c, q in other.final
                for i in range(len(indet_trans))
            ]
        )
        return PGA(
            self.states | new_states, new_transition_matrix, self.initial, self.final
        )

    def decrement(self, indeterminate) -> "PGA":
        dfa_filter = resolve_conflict(self, DFAFactory.neg(DFAFactory.lt("X", 1)))
        filtered = minimize(self.product(dfa_filter))
        subs_zero = minimize(self.substitute("X", 0))
        dfa_s, dfa_t = [el for el in dfa_filter.transition_matrix[indeterminate] if el[0] != el[1]][0]
        new_transition_matrix: dict[str, list[tuple[float, str, str]]] = filtered.transition_matrix.copy()
        for trans in new_transition_matrix[indeterminate]:
            w, s, t = trans
            last_state_s, last_state_t = s.split(",")[-1].split(")")[0], t.split(",")[-1].split(")")[0]
            if last_state_s == dfa_s and last_state_t == dfa_t:
                new_transition_matrix[indeterminate].remove(trans)
                new_transition_matrix[CONSTANT_KEY].append((w, s, t))
        return filtered.weighted_union(subs_zero, 1, 1)
        

def resolve_conflict(a1: Automaton, a2: Automaton) -> Automaton:
    if a1.states.isdisjoint(a2.states):
        return a2
    suffix = "_1"
    while any((s + suffix) in a1.states for s in a2.states):
        suffix += "_"

    rename_map = {s: s + suffix for s in a2.states}

    def rename_set(S):
        # handle weighted and unweighted case
        renamed = set()
        for elem in S:
            if (
                isinstance(elem, tuple)
                and len(elem) == 2
                and not isinstance(elem[0], str)
            ):
                # (weight, state)
                w, s = elem
                renamed.add((w, rename_map.get(s, s)))
            else:
                # plain state
                renamed.add(rename_map.get(elem, elem))
        return renamed

    new_transition_matrix = {}
    for indeterminate, transitions in a2.transition_matrix.items():
        new_entries = []
        for entry in transitions:
            if len(entry) == 2:
                # Unweighted case
                s, t = entry
                new_entries.append((rename_map.get(s, s), rename_map.get(t, t)))
            elif len(entry) == 3:
                weight, s, t = entry
                new_entries.append((weight, rename_map.get(s, s), rename_map.get(t, t)))
            else:
                raise ValueError(f"Weird transition matrix entry {entry}")
        new_transition_matrix[indeterminate] = new_entries
    return Automaton(
        states=rename_set(a2.states),
        transition_matrix=new_transition_matrix,
        initial=rename_set(a2.initial),
        final=rename_set(a2.final),
    )


def minimize(aut: Automaton):
    aut = remove_noncoaccessible_states(aut)
    if isinstance(aut, PGA):
        aut = merge_states(aut)
    return aut


def remove_noncoaccessible_states(aut: Automaton):
    is_pga = isinstance(aut, PGA)

    def get_state(possible_weighted_state):
        return (
            possible_weighted_state[1]
            if isinstance(possible_weighted_state, tuple)
            else possible_weighted_state
        )

    successors = {q: set() for q in aut.states}
    predecessors = {q: set() for q in aut.states}
    print(aut.states)
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
        return PGAFactory.zero()

    new_transition_matrix = dict()
    aut.states = keep
    for indeterminate, transitions in aut.transition_matrix.items():
        keep_trans = []
        for trans in transitions:
            if is_pga:
                w, s, t = trans
                if s in keep and t in keep:
                    keep_trans.append((w, s, t))
            else:
                s, t = trans
                if s in keep and t in keep:
                    keep_trans.append((s, t))
        new_transition_matrix[indeterminate] = keep_trans
    aut.transition_matrix = new_transition_matrix

    if is_pga:
        aut.initial = {(w, s) for (w, s) in aut.initial if s in keep}
        aut.final = {(w, s) for (w, s) in aut.final if s in keep}
    else:
        aut.initial = aut.initial & keep
        aut.final = aut.final & keep

    print(aut)
    return aut


def merge_states(aut: PGA):
    return aut
    if is_minimal(aut):
        return aut
    # todo implement
    pass


def is_minimal(aut: PGA):
    return len(aut.transition_matrix[CONSTANT_KEY]) == 0

# -- Factory --


class PGAFactory:
    def __init__(self, variables):
        self.variables = variables

    @classmethod
    def zero(self):
        return PGA({"q_0"}, dict({v: [] for v in VARIABLES}), {(1, "q_0")}, {})

    @classmethod
    def one(self):
        return PGA(
            {"q_0"}, dict({v: [] for v in VARIABLES}), {(1, "q_0")}, {(1, "q_0")}
        )

    # --- Distributions ---
    @classmethod
    def geometric(self, indeterminate, p) -> PGA:
        return PGA(
            {"q_0"},
            dict(
                {indeterminate: [(1 - p, "q_0", "q_0")]}
                | {v: [] for v in VARIABLES - {indeterminate}}
            ),
            {(1, "q_0")},
            {(p, "q_0")},
        )

    @classmethod
    def dirac(self, indeterminate, n: int) -> PGA:
        return PGA(
            {f"q_{i}" for i in range(n + 1)},
            dict(
                {indeterminate: [(1, f"q_{i}", f"q_{i + 1}") for i in range(n)]}
                | {v: [] for v in VARIABLES - {indeterminate}}
            ),
            {(1, "q_0")},
            {(1, f"q_{n}")},
        )

    @classmethod
    def uniform(self, indeterminate, n: int) -> PGA:
        return PGA(
            {f"q_{i}" for i in range(n - 1)},
            dict(
                {indeterminate: [(1, f"q_{i}", f"q_{i + 1}") for i in range(n - 1)]}
                | {v: [] for v in VARIABLES - {indeterminate}}
            ),
            {(1, "q_0")},
            {(1 / n, f"q_{i}") for i in range(n)},
        )

    @classmethod
    def bernoulli(self, indeterminate, p: float) -> PGA:
        return PGA(
            {"q_0", "q_1"},
            dict(
                {indeterminate: [(p, "q_0", "q_1")]}
                | {v: [] for v in VARIABLES - {indeterminate}}
            ),
            {(1, "q_0")},
            {(1 - p, "q_0"), (1, "q_1")},
        )

    @classmethod
    def neg_binomial(self, indeterminate, n: int, p: float) -> PGA:
        assert n > 0, f"n has to be greater than 0, got {n=}"
        assert 0 <= p and p <= 1, f"p has to be between 0 and 1, got {p=}"

        aut = PGAFactory.geometric(indeterminate, p)
        for _ in range(n - 1):
            aut = aut.concat(PGAFactory.geometric(indeterminate, p))

        return aut


class DFAFactory:
    @classmethod
    def lt(self, indeterminate, val):
        states = {f"p_{i}" for i in range(val + 1)}
        initial = {"p_0"}
        final = {f"p_{i}" for i in range(val)}
        transition_matrix = dict()
        transition_matrix[indeterminate] = [
            (f"p_{i}", f"p_{i + 1}") for i in range(val)
        ] + [(f"p_{val}", f"p_{val}")]
        transition_matrix = reflexive_closure(
            transition_matrix, VARIABLES - {indeterminate}, states
        )
        return DFA(states, transition_matrix, initial, final)

    @classmethod
    def mod(self, indeterminate, modulus, residue):
        assert modulus > residue, "Modulus has to be greater than residue."
        states = {f"q_{i}" for i in range(modulus)}
        initial = {"q_0"}
        final = {f"q_{residue}"}
        transition_matrix = dict()
        transition_matrix[indeterminate] = [
            (f"q_{i}", f"q_{i + 1}") for i in range(modulus - 1)
        ] + [(f"q_{modulus - 1}", "q_0")]
        transition_matrix = reflexive_closure(
            transition_matrix, VARIABLES - {indeterminate}, states
        )
        return DFA(states, transition_matrix, initial, final)

    # -------- Syntactic Sugar --------------
    @classmethod
    def eq(self, indeterminate, val):
        states = {f"p_{i}" for i in range(val + 2)}
        initial = {"p_0"}
        final = {f"p_{val}"}
        transition_matrix = dict()
        transition_matrix[indeterminate] = [
            (f"p_{i}", f"p_{i + 1}") for i in range(val + 1)
        ] + [(f"p_{val + 1}", f"p_{val + 1}")]
        transition_matrix = reflexive_closure(
            transition_matrix, VARIABLES - {indeterminate}, states
        )
        return DFA(states, transition_matrix, initial, final)

    @classmethod
    def neg(self, dfa: DFA):
        return DFA(
            dfa.states, dfa.transition_matrix, dfa.initial, dfa.states - dfa.final
        )

    @classmethod
    def land(self, dfa1: DFA, dfa2: DFA):
        states = set(itertools.product(dfa1.states, dfa2.states))
        initial = set(itertools.product(dfa1.initial, dfa2.initial))
        final = set(itertools.product(dfa1.final, dfa2.final))
        transition_matrix = dict()
        for v in VARIABLES:
            transition_matrix[v] = [
                (f"({state1}, {state2})", f"({state3}, {state4})")
                for (state1, state3) in dfa1.transition_matrix[v]
                for (state2, state4) in dfa2.transition_matrix
            ]
        return DFA(states, transition_matrix, initial, final)


def reflexive_closure(transition_matrix, variables, states):
    for v in variables:
        transition_matrix[v] = [(q, q) for q in states]
    return transition_matrix

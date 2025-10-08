import itertools
from abc import ABC, abstractmethod

CONSTANT_KEY = 1


class Automaton(ABC):
    """Represents the abstract notion of an automaton.
    """
    def __init__(self, states: set[str], transition_matrix: dict[tuple], initial: set, final: set):
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
    def __init__(self, states, transition_matrix:dict[str, list[tuple[str, str]]], initial: set[str], final:set[str]):
        super().__init__(states, transition_matrix, initial, final)
    

class PGA(Automaton):
    def __init__(self, states, transition_matrix: dict[str, list[tuple[float, str, str]]], initial: set[tuple[float,str]], final: set[tuple[float,str]]):
        return super().__init__(states, transition_matrix, initial, final)
    
    def substitute(self, indeterminate, value: int) -> "PGA":
        """Substitutes a given indeterminate by some value in {0,1}

        Args:
            indeterminate (str): The indeterminate to be substituted
            value (int): The value (0 or 1).

        Returns:
            PGA: The substitution PGA A[X/i].
        """
        assert value in {0, 1}, f"Substitution is only supported for 0 or 1, got {value}"
        new_transition_matrix = self.transition_matrix
        new_transition_matrix[indeterminate] = []
        new_transition_matrix[CONSTANT_KEY].extend(self.transition_matrix[indeterminate] if indeterminate == 1 else [])         
        return PGA(
            self.states,
            new_transition_matrix,
            self.initial,
            self.final
        )
    
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
            new_transition_matrix[k] =  self.transition_matrix[k] + other.transition_matrix[k]
        if CONSTANT_KEY in new_transition_matrix:
            new_transition_matrix[CONSTANT_KEY] += [(c1*c2, from_state, to_state) for ((c1, from_state), (c2,to_state)) in set(itertools.product(self.final, other.initial))]
        else:
            new_transition_matrix[CONSTANT_KEY] = [(c1*c2, from_state, to_state) for ((c1, from_state), (c2,to_state)) in set(itertools.product(self.final, other.initial))]
        return PGA(
            self.states | other.states,
            new_transition_matrix,
            self.initial,
            other.final
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
        assert 0 <= p and p <= 1 and 0 <= q and q <= 1, f"p and q have to be between 0 and 1 , got {p=} and {q=}"
        if not self.states.isdisjoint(other.states):
            other = resolve_conflict(self, other)
        new_initial = {(p*c, state) for (c, state) in self.initial} | {(q*c, state) for (c,state) in other.initial}
        new_transition_matrix = dict()
        for k in self.transition_matrix.keys() | other.transition_matrix.keys():
            new_transition_matrix[k] = (self.transition_matrix[k] if k in self.transition_matrix else []) \
                + (other.transition_matrix[k] if k in other.transition_matrix else [])
        return PGA(
            self.states | other.states,
            new_transition_matrix,
            new_initial,
            self.final | other.final
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
            new_transition_matrix[v] = [(c, f"({state1},{state2})", f"({state3},{state4})") for (c, state1, state3) in s_trans for (state2, state4) in o_trans] 
        new_initial = set((c, f"({state1},{state2})") for (c,state1) in self.initial for state2 in other.initial)
        new_final = set((c, f"({state1},{state2})") for (c,state1) in self.final for state2 in other.final)
        
        return PGA(
            new_states,
            new_transition_matrix,
            new_initial,
            new_final
        )
    
    def transition_substitution(self, indeterminate, other: "PGA") -> "PGA":
        """Substitutes all indeterminates of the PGA by the other PGA.

        Args:
            indeterminate (str): The indeterminate to be substituted. 
            other (PGA): The PGA that should be inserted for each transition containing the indeterminate.

        Returns:
            PGA: The PGA A_1[Y/A_2].
        """
        indet_trans = self.transition_matrix[indeterminate]
        new_states = set([f"{q}_{i}" for q in other.states for i in range(len(indet_trans))])
        if not self.states.isdisjoint(other.states):
            other = resolve_conflict(self, other)
        
        new_transition_matrix = self.transition_matrix.copy()
        new_transition_matrix[indeterminate] = []
        
        
        for v in other.transition_matrix.keys():
            if other.transition_matrix[v]:
                new_transition_matrix[v] += [
                    (c,  f"{state1}_{i}",  f"{state2}_{i}") for i in range(len(indet_trans)) for (c,state1,state2) in other.transition_matrix[v]
                ]
        new_transition_matrix[CONSTANT_KEY].extend([
            (indet_trans[i][0] * c, indet_trans[i][1], f"{q}_{i}") for i in range(len(indet_trans)) for c, q in other.initial  
        ] + [(c, f"{q}_{i}", indet_trans[i][2] ) for c, q in other.final for i in range(len(indet_trans))])
        return PGA(
            self.states | new_states,
            new_transition_matrix,
            self.initial,
            self.final
        )
    
def resolve_conflict(a1: Automaton, a2: Automaton) -> Automaton:
    suffix = "_1"
    while any((s + suffix) in a1.states for s in a2.states):
        suffix += "_"
    
    rename_map = {s: s + suffix for s in a2.states}
    
    def rename_set(S):
        # handle weighted and unweighted case
        renamed = set()
        for elem in S:
            if isinstance(elem, tuple) and len(elem) == 2 and not isinstance(elem[0], str):
                # (weight, state)
                w, s = elem
                renamed.add((w, rename_map.get(s,s)))
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
                s,t = entry
                new_entries.append((rename_map.get(s,s), rename_map.get(t,t)))
            elif len(entry) == 3:
                weight, s, t = entry
                new_entries.append((weight,rename_map.get(s,s), rename_map.get(t,t)))
            else:
                raise ValueError(f"Weird transition matrix entry {entry}")
        new_transition_matrix[indeterminate] = new_entries    
    return Automaton(
        states=rename_set(a2.states),
        transition_matrix=new_transition_matrix,
        initial=rename_set(a2.initial),
        final=rename_set(a2.final)
    )
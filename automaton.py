import itertools
from abc import ABC, abstractmethod

CONSTANT_KEY = 1

class State:
    def __init__(self, name):
        self.name = name
        
    def rename(self, new_name):
        self.name = new_name
        
    def __str__(self):
        return str(self.name)
    
    def __eq__(self, value):
        if not isinstance(value, State):
            return False
        return self.name == value.name

class Automaton(ABC):
    """Represents the abstract notion of an automaton.
    """
    def __init__(self, states: set[State], transition_matrix: dict, initial: set, final: set):
        self.states = states
        self.transition_matrix = transition_matrix
        self.initial = initial
        self.final = final

    def __str__(self):
        return f"States: {self.states}, Transition matrix: {self.transition_matrix}, Initial: {self.initial}, Final: {self.final}"
    
class DFA(Automaton):
    """A DFA (deterministic finite automaton). Instantiation of Automaton.
    """
    def __init__(self, states, transition_matrix:dict[str, list[tuple[State, State]]], initial: set[State], final:set[State]):
        super().__init__(states, transition_matrix, initial, final)
    

class PGA(Automaton):
    def __init__(self, states, transition_matrix: dict[str, list[tuple[float, State, State]]], initial: set[tuple[float,State]], final: set[tuple[float,State]]):
        return super().__init__(states, transition_matrix, initial, final)
    
    def substitute(self, indeterminate, value: int) -> "PGA":
        """Substitutes a given indeterminate by some value \in {0,1}

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
        print(f"Concatenating {self}, {other}")
        if not self.states.isdisjoint(other.states):
            other = fix_name_conflict(self, other)
            # todo rename
        new_transition_matrix = self.transition_matrix
        new_transition_matrix[CONSTANT_KEY].extend(
            [(1, from_state, to_state) for ((_, from_state), (_,to_state)) in set(itertools.product(self.final, other.initial))]
        )
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
            pass # todo rename
        new_initial = {(p*c, state) for (c, state) in self.intitial} + {(q*c, state) for (c,state) in other.initial}
        new_transition_matrix = dict()
        for k in self.transition_matrix.keys() | other.transition_matrix.keys():
            new_transition_matrix[k] = (self.transition_matrix[k] if k in self.transition_matrix else []) \
                + (other.transition_matrix[k] if k in other.transition_matrix else [])
        return PGA(
            self.states | other.states,
            new_transition_matrix,
            new_initial,
            self.final + other.final
        )
        
    def product(self, other: DFA) -> "PGA":
        """Filters the PGA by a given DFA.

        Args:
            other (DFA): The DFA the PGA should by filtered by.

        Returns:
            PGA: The filtered PGA A x B_\phi.
        """
        if not self.states.isdisjoint(other.states):
            pass # todo rename
        new_states = {f"({q1,q2})" for q1 in self.states for q2 in other.states}
        new_transition_matrix = dict()
        for v in self.transition_matrix.keys():
            print(v, self.transition_matrix[v], other.transition_matrix[v])
            new_transition_matrix[v] = [(c, f"({state1},{state2})", f"({state3},{state4})") for (c, state1, state3) in self.transition_matrix[v] for (state2, state4) in other.transition_matrix[v]] 
            print(new_transition_matrix[v])
        print(self.initial)
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
            pass # todo rename
        new_transition_matrix = self.transition_matrix
        new_transition_matrix[indeterminate] = []
        for v in self.transition_matrix.keys():
            new_transition_matrix[v] += [
                (c, state1 + f"_{i}", state2 + "_{i}") for (c,state1,state2) in other.transition_matrix for i in range(len(indet_trans))
            ]
        new_transition_matrix[CONSTANT_KEY].extend([
            (indet_trans[i][0], indet_trans[i][1], f"{q}_{i}") for i in range(len(indet_trans)) for q in other.initial  
        ])
        return PGA(
            new_states,
            new_transition_matrix,
            self.initial,
            self.final
        )
    
def fix_name_conflict(aut1: Automaton, aut2: Automaton) -> tuple[Automaton, Automaton]:
    # TODO sensible name conflict resolution
    violating_states = aut1.states.intersection(aut2.states)
    for state in violating_states:
        s = aut2.states.intersection(state).pop()
        s.rename(state.name + "_1")
    
    return (aut1, aut2)
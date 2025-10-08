from automaton import PGA, DFA
import itertools

VARIABLES = {"X", "Y", "Z", 1}

# TODO Remove hardcoded names

class PGAFactory:
    def __init__(self, variables):
        self.variables = variables
    @classmethod
    def zero(self):
        return PGA(
            {"q_0"},
            dict({v: [] for v in VARIABLES}),
            {(1, "q_0")},
            {}
        )
    
    @classmethod
    def one(self):
        return PGA(
            {"q_0"},
            dict({v: [] for v in VARIABLES}),
            {(1, "q_0")},
            {(1,"q_0")}
        )
    
    # --- Distributions ---
    @classmethod
    def geometric(self, indeterminate, p) -> PGA:
        return PGA(
            {"q_0"},
            dict({indeterminate: [(1-p, "q_0", "q_0")]} | {v: [] for v in VARIABLES - {indeterminate}}),
            {(1, "q_0")},
            {(p, "q_0")}
        )
    
    @classmethod
    def dirac(self, indeterminate, n: int) -> PGA:
        return PGA(
            {f"q_{i}" for i in range(n + 1)},
            dict({indeterminate: [(1, f"q_{i}", f"q_{i+1}") for i in range(n)]} | {v: [] for v in VARIABLES - {indeterminate}}),
            {(1, "q_0")},
            {(1, f"q_{n}")}
        )
    
    @classmethod
    def uniform(self, indeterminate, n: int) -> PGA:
        return PGA(
            {f"q_{i}" for i in range(n-1)},
            dict({indeterminate: [(1, f"q_{i}", f"q_{i+1}") for i in range(n-1)]} | {v: [] for v in VARIABLES - {indeterminate}}),
            {(1, "q_0")},
            {(1/n, f"q_{i}") for i in range(n) }
        )
    
    @classmethod
    def bernoulli(self, indeterminate, p: float) -> PGA:
        return PGA(
            {"q_0", "q_1"},
            dict({indeterminate: [(p, "q_0", "q_1")]} | {v: [] for v in VARIABLES - {indeterminate}}),
            {(1, "q_0")},
            {(1-p, "q_0"), (1, "q_1")}
        )
    
    @classmethod
    def neg_binomial(self, indeterminate, n: int, p: float) -> PGA:
        assert n > 0, f"n has to be greater than 0, got {n=}"
        assert 0 <= p and p <= 1, f"p has to be between 0 and 1, got {p=}"
        
        aut = PGAFactory.geometric(indeterminate, p)
        for _ in range(n):
            aut = aut.concat(PGAFactory.geometric(indeterminate, p))
            
        return aut
            
    
    
    
class DFAFactory:
    @classmethod
    def lt(self, indeterminate, val):
        states = {f"p_{i}" for i in range(val + 1)}
        initial = {"p_0"}
        final = {f"p_{i}" for i in range(val)}
        transition_matrix = dict()
        transition_matrix[indeterminate] = \
            [(f"p_{i}", f"p_{i+1}") for i in range(val)] + [(f"p_{val}", f"p_{val}")]
        transition_matrix = reflexive_closure(transition_matrix, VARIABLES - {indeterminate}, states)
        return DFA(
            states,
            transition_matrix,
            initial,
            final
        )
    
    @classmethod
    def mod(self, indeterminate, modulus, residue):
        assert modulus > residue, "Modulus has to be greater than residue."
        states = {f"q_{i}" for i in range(modulus)}
        initial = {"q_0"}
        final = {f"q_{residue}"}
        transition_matrix = dict()
        transition_matrix[indeterminate] = \
            [(f"q_{i}", f"q_{i+1}") for i in range(modulus -1 )] + [(f"q_{modulus - 1}", "q_0")]
        transition_matrix = reflexive_closure(transition_matrix, VARIABLES - {indeterminate}, states)
        return DFA(
            states,
            transition_matrix,
            initial,
            final
        )
        
    # -------- Syntactic Sugar --------------
    @classmethod
    def eq(self, indeterminate, val):
        states = {f"p_{i}" for i in range(val + 2)}
        initial = {"p_0"}
        final = {f"p_{val}"}
        transition_matrix = dict()
        transition_matrix[indeterminate] = \
            [(f"p_{i}", f"p_{i+1}") for i in range(val+1)] + [(f"p_{val+1}", f"p_{val+1}")]
        transition_matrix = reflexive_closure(transition_matrix, VARIABLES - {indeterminate}, states)
        return DFA(
            states,
            transition_matrix,
            initial,
            final
        )
    
    @classmethod
    def neg(self, dfa: DFA):
        return DFA(
            dfa.states,
            dfa.transition_matrix,
            dfa.initial,
            dfa.states - dfa.final 
        )
    
    @classmethod
    def land(self, dfa1: DFA, dfa2: DFA):
        states = set(itertools.product(dfa1.states, dfa2.states))
        initial = set(itertools.product(dfa1.initial, dfa2.initial))
        final = set(itertools.product(dfa1.final, dfa2.final))
        transition_matrix = dict()
        for v in VARIABLES:
            transition_matrix[v] = [(f"({state1}, {state2})", f"({state3}, {state4})") for (state1, state3) in dfa1.transition_matrix[v] for (state2, state4) in dfa2.transition_matrix]
        return DFA(
            states,
            transition_matrix,
            initial,
            final
        )
    
def reflexive_closure(transition_matrix, variables, states):
    for v in variables:
        transition_matrix[v] = [(q, q) for q in states]
    return transition_matrix

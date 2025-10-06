from automaton import DFA
from abc import ABC, abstractmethod
from automata_factory import DFAFactory

class Guard(ABC):
    @abstractmethod
    def to_dfa(self) -> DFA: 
        pass

    
class LtGuard(Guard):
    def __init__(self, indeterminate, n: int):
        self.indeterminate = indeterminate
        self.n = n
    
    def to_dfa(self) -> DFA:
        return DFAFactory.lt(self.indeterminate, self.n)
    
    def __str__(self):
        return f"{self.indeterminate} < {self.n}"
    
class ModGuard(Guard):
    def __init__(self, indeterminate, modulus: int, residue: int):
        assert modulus > residue, f"Modulus has to be greater than residue, got: {modulus=}, {residue=}"
        self.indeterminate = indeterminate
        self.modulus = modulus
        self.residue = residue
        
    def to_dfa(self):
        return DFAFactory.mod(self.indeterminate, self.modulus, self.residue)
        
    def __str__(self):
        return f"{self.indeterminate} mod {self.modulus} = {self.residue}"
    
class NegGuard(Guard):
    def __init__(self, guard: Guard):
        self.guard = guard
        
    def to_dfa(self):
        return DFAFactory.neg(self.guard.to_dfa())
    
    def __str__(self):
        return f"¬({self.guard})"
    

class LandGuard(Guard):
    def __init__(self, guard1: Guard, guard2: Guard):
        self.guard1 = guard1
        self.guard2 = guard2
        
    def to_dfa(self):
        return DFAFactory.land(self.guard1.to_dfa(), self.guard2.to_dfa())
    
    def __str__(self):
        return f"({self.guard1}) && ({self.guard2})"
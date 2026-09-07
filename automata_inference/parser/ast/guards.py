from dataclasses import dataclass


class Guard:
    """Base class for guards."""


@dataclass(frozen=True)
class LessThan(Guard):
    """Models the guard `variable` < `value`.
    
    Args:
        variable (str): The variable to be compared.
        value (int): The value the variable should be compared against.
    """
    variable: str
    value: int
    
    def __str__(self):
        return f"{self.variable} < {self.value}"
    
@dataclass(frozen=True)
class ModuloEquals(Guard):
    """Models the guard `variable` mod `modulus` = `residue`.
        
    Args:
        variable (str): The variable to be compared.
        modulus (int): The modulus of the operation.
        residue (int): The residue of the operation.
    """
    variable: str
    modulus: int
    residue: int
    
    def __str__(self):
        return f"{self.variable} mod {self.modulus} = {self.residue}"


@dataclass(frozen=True)
class Equals(Guard):
    """Models the guard `variable` = `value`.
    
    Args:
        variable (str): The variable to be compared.
        value (int): The value the variable should be compared against.
    """
    variable: str
    value: int
    
    def __str__(self):
        return f"{self.variable} = {self.value}"


@dataclass(frozen=True)
class Not(Guard):
    """Models the negation of a guard.
    
    Args:
        guard (Guard): The guard to be negated.
    """
    guard: Guard
    
    def __str__(self):
        return f"!({self.guard})"


@dataclass(frozen=True)
class And(Guard):
    """Models the logical conjunction of two guard.
    
    Args:
        left (Guard): The left-hand side of the conjunction.
        right (Guard): The right-hand side of the conjunction.
    """
    left: Guard
    right: Guard
    
    def __str__(self):
        return f"({self.left} && {self.right})"


@dataclass(frozen=True)
class Or(Guard):
    """Models the logical disjunction of two guard.
    
    Args:
        left (Guard): The left-hand side of the disjunction.
        right (Guard): The right-hand side of the disjunction.
    """
    left: Guard
    right: Guard
    
    def __str__(self):
            return f"({self.left} || {self.right})"


@dataclass(frozen=True)
class Implies(Guard):
    """Models the logical implication of two guard.
    
    Args:
        left (Guard): The left-hand side of the implication.
        right (Guard): The right-hand side of the implication.
    """
    left: Guard
    right: Guard
    
    def __str__(self):
            return f"({self.left} -> {self.right})"
    

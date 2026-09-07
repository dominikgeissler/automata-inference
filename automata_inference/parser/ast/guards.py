from dataclasses import dataclass


class Guard:
    """Base class for guards."""


@dataclass(frozen=True)
class LessThan(Guard):
    variable: str
    value: int
    
    def __str__(self):
        return f"{self.variable} < {self.value}"


@dataclass(frozen=True)
class ModuloEquals(Guard):
    variable: str
    modulus: int
    residue: int
    
    def __str__(self):
        return f"{self.variable} mod {self.modulus} = {self.residue}"


@dataclass(frozen=True)
class Equals(Guard):
    variable: str
    value: int
    
    def __str__(self):
        return f"{self.variable} = {self.value}"


@dataclass(frozen=True)
class Not(Guard):
    guard: Guard
    
    def __str__(self):
        return f"!({self.guard})"


@dataclass(frozen=True)
class And(Guard):
    left: Guard
    right: Guard
    
    def __str__(self):
        return f"({self.left} && {self.right})"


@dataclass(frozen=True)
class Or(Guard):
    left: Guard
    right: Guard
    
    def __str__(self):
            return f"({self.left} || {self.right})"


@dataclass(frozen=True)
class Implies(Guard):
    left: Guard
    right: Guard
    
    def __str__(self):
            return f"({self.left} -> {self.right})"
    

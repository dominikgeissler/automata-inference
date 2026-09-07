from __future__ import annotations

from dataclasses import dataclass

from symengine import Rational

from automata_inference.parser.ast.distributions import Distribution
from automata_inference.parser.ast.guards import Guard
from automata_inference.parser.ast.queries import Query


class Statement:
    """Base class for parsed statements."""


class Rhs:
    """Base class for right-hand side of an assignment or increment."""


@dataclass(frozen=True)
class ConstantRhs(Rhs):
    value: int
    
    def __str__(self):
        return str(self.value)


@dataclass(frozen=True)
class VariableRhs(Rhs):
    variable: str
    
    def __str__(self):
            return str(self.variable)


@dataclass(frozen=True)
class DistributionRhs(Rhs):
    distribution: Distribution
    
    def __str__(self):
            return str(self.distribution)


@dataclass(frozen=True)
class IidRhs(Rhs):
    distribution: Distribution
    variable: str
    
    def __str__(self):
            return f"iid({self.distribution}, {self.variable})"


@dataclass(frozen=True)
class SkipStatement(Statement):
    pass

    def __str__(self):
         return "skip"


@dataclass(frozen=True)
class AssignStatement(Statement):
    variable: str
    rhs: Rhs
    
    def __str__(self):
         return f"{self.variable} := {self.rhs}"


@dataclass(frozen=True)
class IncrementStatement(Statement):
    variable: str
    rhs: Rhs
    
    def __str__(self):
             return f"{self.variable} += {self.rhs}"
    


@dataclass(frozen=True)
class MonusStatement(Statement):
    variable: str
    
    def __str__(self):
         return f"{self.variable}--"


@dataclass(frozen=True)
class CoinflipStatement(Statement):
    left: Statement
    p: Rational
    right: Statement
    
    def __str__(self):
         return f"{{ {self.left} }} [{self.p}] {{ {self.right} }}"


@dataclass(frozen=True)
class IfStatement(Statement):
    guard: Guard
    then_statement: Statement
    else_statement: Statement | None = None

    def __str__(self):
         return f"if ({self.guard}) {{ {self.then_statement} }}" + f" else {{ {self.else_statement} }}" if self.else_statement else ""



@dataclass(frozen=True)
class ObserveStatement(Statement):
    guard: Guard
    
    def __str__(self):
         return f"observe ({self.guard})"


@dataclass(frozen=True)
class SequentialCompositionStatement(Statement):
    left: Statement
    right: Statement
    
    def __str__(self):
         return f"{self.left} ; {self.right}"


@dataclass(frozen=True)
class Program:
    body: Statement | None
    is_observe: bool
    variables: set[str]
    query: Query | None = None

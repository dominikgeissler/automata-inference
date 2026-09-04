from __future__ import annotations

from dataclasses import dataclass
from symengine import Rational

from automata_inference.parser.ast.guards import Guard
from automata_inference.parser.ast.distributions import Distribution
from automata_inference.parser.ast.queries import Query

class Statement:
    """Base class for parsed statements."""


class Rhs:
    """Base class for right-hand side of an assignment or increment."""


@dataclass(frozen=True)
class ConstantRhs(Rhs):
    value: int


@dataclass(frozen=True)
class VariableRhs(Rhs):
    variable: str


@dataclass(frozen=True)
class DistributionRhs(Rhs):
    distribution: Distribution


@dataclass(frozen=True)
class IidRhs(Rhs):
    distribution: Distribution
    variable: str


@dataclass(frozen=True)
class SkipStatement(Statement):
    pass


@dataclass(frozen=True)
class AssignStatement(Statement):
    variable: str
    rhs: Rhs


@dataclass(frozen=True)
class IncrementStatement(Statement):
    variable: str
    rhs: Rhs


@dataclass(frozen=True)
class MonusStatement(Statement):
    variable: str


@dataclass(frozen=True)
class CoinflipStatement(Statement):
    left: Statement
    p: Rational
    right: Statement


@dataclass(frozen=True)
class IfStatement(Statement):
    guard: Guard
    then_statement: Statement
    else_statement: Statement | None = None


@dataclass(frozen=True)
class ObserveStatement(Statement):
    guard: Guard


@dataclass(frozen=True)
class SequentialCompositionStatement(Statement):
    left: Statement
    right: Statement


@dataclass(frozen=True)
class Program:
    body: Statement | None
    is_observe: bool
    variables: frozenset[str]
    query: Query | None = None
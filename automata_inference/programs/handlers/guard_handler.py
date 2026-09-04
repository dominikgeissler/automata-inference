from automata_inference.parser.ast.guards import (
    Guard,
    Equals,
    LessThan,
    Not,
    ModuloEquals,
    Implies,
    And,
    Or,
)
from automata_inference.automata.model import DFA
from automata_inference.automata.factory import DFAFactory


class GuardHandler:

    def __init__(self, indeterminates: frozenset[str]):
        self.indeterminates = indeterminates

    def compile(self, guard: Guard) -> DFA:
        if isinstance(guard, LessThan):
            return DFAFactory.lt(guard.variable, guard.value, self.indeterminates)
        if isinstance(guard, ModuloEquals):
            return DFAFactory.mod(
                guard.variable, guard.modulus, guard.residue, self.indeterminates
            )
        if isinstance(guard, Equals):
            return DFAFactory.eq(guard.variable, guard.value, self.indeterminates)
        if isinstance(guard, And):
            return DFAFactory.land(self.compile(guard.left), self.compile(guard.right))
        if isinstance(guard, Not):
            return DFAFactory.neg(self.compile(guard.guard))
        if isinstance(guard, Implies):
            return DFAFactory.neg(
                DFAFactory.land(
                    self.compile(guard.left),
                    DFAFactory.neg(self.compile(guard.right)),
                )
            )
        if isinstance(guard, Or):
            return DFAFactory.neg(
                DFAFactory.land(
                    DFAFactory.neg(self.compile(guard.left)),
                    DFAFactory.neg(self.compile(guard.right)),
                )
            )
        raise ValueError(f"Unsupported guard type: {type(guard)}")

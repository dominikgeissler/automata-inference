from automata_inference.automata.factory import DFAFactory
from automata_inference.automata.model import DFA
from automata_inference.parser.ast.guards import (
    And,
    Equals,
    Guard,
    Implies,
    LessThan,
    ModuloEquals,
    Not,
    Or,
)


class GuardHandler:
    """Transforms a parsed guard into a DFA."""

    def __init__(self, indeterminates: set[str]):
        """Creates a new GuardHandler instance.

        Args:
            indeterminates (set[str]): The set of indeterminates within the program.
        """
        self.indeterminates = indeterminates

    def compile(self, guard: Guard) -> DFA:
        """Transforms a guard into its DFA represntation.

        Args:
            guard (Guard): The guard to transform into a DFA.

        Raises:
            ValueError: If the guard type is unsupported.

        Returns:
            DFA: The DFA representation of the guard.
        """
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

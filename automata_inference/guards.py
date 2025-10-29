from abc import ABC, abstractmethod
from automata_inference.automata_factory import DFAFactory, DFA

from automata_inference.program_context import ProgramContext


class Guard(ABC):
    """Models Boolean guards."""

    @abstractmethod
    def to_dfa(self, context: ProgramContext) -> DFA:
        """Converts the given guard to the DFA representation.


        Args:
            context (ProgramContext): The program context.

        Returns:
            DFA: The DFA representing the guard.
        """


class LtGuard(Guard):
    """
    Less-than Guard.
    """

    def __init__(self, indeterminate: str, n: int):
        """Creates a new LtGuard `indeterminate` < `n`.

        Args:
            indeterminate (str): The indeterminate.
            n (int): The value.
        """
        self.indeterminate = indeterminate
        self.n = n

    def to_dfa(self, context) -> DFA:
        return DFAFactory.lt(self.indeterminate, self.n, context.indeterminates)

    def __str__(self):
        return f"{self.indeterminate} < {self.n}"


class ModGuard(Guard):
    """
    Modulus guard.
    """

    def __init__(self, indeterminate: str, modulus: int, residue: int):
        """Creates a mew ModGuard `ìndeterminate` mod `modulus` = `residue`.
        Args:
            indeterminate (str): The indeterminate.
            modulus (int): The modulus of the comparison.
            residue (int): The residue of the operation.
        """
        assert modulus > residue, f"Modulus has to be greater than residue, got: {modulus=}, {residue=}"
        self.indeterminate = indeterminate
        self.modulus = modulus
        self.residue = residue

    def to_dfa(self, context):
        return DFAFactory.mod(self.indeterminate, self.modulus, self.residue, context.indeterminates)

    def __str__(self):
        return f"{self.indeterminate} mod {self.modulus} = {self.residue}"


class NegGuard(Guard):
    """
    Negation of a guard.
    """

    def __init__(self, guard: Guard):
        """Creates a new NegGuard ¬(`guard`).

        Args:
            guard (Guard): The guard to be negated.
        """
        self.guard = guard

    def to_dfa(self, context):
        return DFAFactory.neg(self.guard.to_dfa(context))

    def __str__(self):
        return f"¬({self.guard})"


class LandGuard(Guard):
    """
    Conjunction of two guards.
    """

    def __init__(self, guard1: Guard, guard2: Guard):
        """Creates a new LandGuard (`guard1` && `guard2`)

        Args:
            guard1 (Guard): The first guard (lhs of the land).
            guard2 (Guard): The second guard (rhs of the land).
        """
        self.guard1 = guard1
        self.guard2 = guard2

    def to_dfa(self, context):
        return DFAFactory.land(self.guard1.to_dfa(context), self.guard2.to_dfa(context), context.indeterminates)

    def __str__(self):
        return f"({self.guard1}) && ({self.guard2})"


# ----------------- Syntactic Sugar ---------------


class EqGuard(Guard):
    """Represents the equality guard `indeterminate = n`"""

    def __init__(self, indeterminate: str, n: int):
        """Creates a new EqGuard `indeterminate = n`.

        Args:
            indeterminate (str): The indeterminate.
            n (int): The value the indeterminates count should be equal to.
        """
        self.indeterminate = indeterminate
        self.n = n

    def to_dfa(self, context):
        return DFAFactory.eq(self.indeterminate, self.n, context.indeterminates)

    def __str__(self):
        return f"{self.indeterminate} = {self.n}"

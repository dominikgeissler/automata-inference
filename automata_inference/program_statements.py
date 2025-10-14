from abc import ABC, abstractmethod

from automata_inference.guards import Guard
from automata_inference.distributions import Distribution, DiracDistribution
from automata_inference.automata_factory import PGAFactory, DFAFactory, PGA


class Statement(ABC):
    """Represents a program statement."""
    @abstractmethod
    def apply_semantics(self, pga: PGA) -> PGA:
        """Computes the semantics of the program statement.

        Args:
            pga (PGA): The input PGA.

        Returns:
            PGA: The result of the semantics.
        """


# Todo one assignment statement?


class SetToZeroStatement(Statement):
    """The set to zero statement `indeterminate := 0`.
    """
    def __init__(self, indeterminate):
        self.indeterminate = indeterminate

    def apply_semantics(self, pga) -> PGA:
        print(f"Calculating {str(self)}...")
        return pga.substitute(self.indeterminate, 1)

    def __str__(self):
        return f"{self.indeterminate} := 0"


class IncrementConstantStatement(Statement):
    """The increment constant statement `indeterminate += n`.
    """
    def __init__(self, indeterminate, n: int):
        self.indeterminate = indeterminate
        self.n = n

    # Special case -> Join?
    def apply_semantics(self, pga) -> PGA:
        print(f"Calculating {str(self)}...")
        return IncrementDistributionStatement(
            self.indeterminate, DiracDistribution(self.indeterminate, self.n)
        ).apply_semantics(pga)

    def __str__(self):
        return f"{self.indeterminate} += {self.n}"


class IncrementDistributionStatement(Statement):
    """The increment distribution statement `indeterminate += distribution`.
    """
    def __init__(self, indeterminate, distribution: Distribution):
        self.indeterminate = indeterminate
        self.distribution = distribution

    def apply_semantics(self, pga) -> PGA:
        print(f"Calculating {str(self)}...")
        return pga.concat(self.distribution.to_pga())

    def __str__(self):
        return f"{self.indeterminate} += {self.distribution}"


class IncrementVariableStatement(Statement):
    """The increment variable statement `indeterminate_lhs += indeterminate_rhs`.
    """
    def __init__(self, indeterminate_lhs, indeterminate_rhs):
        self.indeterminate_lhs = indeterminate_lhs
        self.indeterminate_rhs = indeterminate_rhs

    # Special case -> Join?
    def apply_semantics(self, pga) -> PGA:
        print(f"Calculating {str(self)}...")
        return IidSamplingStatement(
            self.indeterminate_lhs,
            DiracDistribution(self.indeterminate_lhs, 1),
            self.indeterminate_rhs,
        ).apply_semantics(pga)

    def __str__(self):
        return f"{self.indeterminate_lhs} += {self.indeterminate_rhs}"


class IidSamplingStatement(Statement):
    """The iid statement `indeterminate_lhs += iid(distribution, indeterminate_rhs)`.
    """
    def __init__(
        self, indeterminate_lhs, distribution: Distribution, indeterminate_rhs
    ):
        self.indeterminate_lhs = indeterminate_lhs
        self.distribution = distribution
        self.indeterminate_rhs = indeterminate_rhs

    def apply_semantics(self, pga) -> PGA:
        print(f"Calculating {str(self)}...")
        return pga.transition_substitution(
            self.indeterminate_rhs,
            PGAFactory.dirac(self.indeterminate_rhs, 1).concat(
                self.distribution.to_pga()
            ),
        )

    def __str__(self):
        return f"{self.indeterminate_lhs} += iid({self.distribution}, {self.indeterminate_rhs})"


class CoinflipStatement(Statement):
    """The coinflip statement `{ lhs } [p] { rhs }`.
    """
    def __init__(self, lhs: Statement, p: float, rhs: Statement):
        assert 0 <= p <= 1, f"p has to be between 0 and 1, got {p=}"
        self.lhs = lhs
        self.p = p
        self.rhs = rhs

    def apply_semantics(self, pga) -> PGA:
        print(f"Calculating {str(self)}...")
        return self.lhs.apply_semantics(pga).weighted_union(
            self.rhs.apply_semantics(pga), self.p, 1 - self.p
        )

    def __str__(self):
        return f"{{ {self.lhs} }} [{self.p}] {{ {self.rhs} }}"


class IfStatement(Statement):
    """The if statement `if(guard) { then_statenent } else { else_statement }`.
    """
    def __init__(
        self, guard: Guard, then_statement: Statement, else_statement: Statement
    ):
        self.guard = guard
        self.then_statement = then_statement
        self.else_statement = else_statement

    def apply_semantics(self, pga) -> PGA:
        print(f"Calculating {str(self)}...")
        guard_dfa = self.guard.to_dfa()
        neg_guard_dfa = DFAFactory.neg(guard_dfa)
        return self.then_statement.apply_semantics(
            pga.product(guard_dfa)
        ).weighted_union(
            self.else_statement.apply_semantics(pga.product(neg_guard_dfa)), 1, 1
        )

    def __str__(self):
        return f"if({self.guard}) then {{ {self.then_statement} }} else {{ {self.else_statement} }}"


class MonusStatement(Statement):
    """The monus statement `indeterminate--`.
    """
    def __init__(self, indeterminate):
        self.indeterminate = indeterminate

    def apply_semantics(self, pga) -> PGA:
        return pga.decrement(self.indeterminate)

    def __str__(self):
        return f"{self.indeterminate}--"


class ObserveStatement(Statement):
    """The observe statement `observe(guard)`.
    """
    def __init__(self, guard: Guard):
        self.guard = guard

    def apply_semantics(self, pga: PGA) -> PGA:
        print(f"Calculating {str(self)}...")
        return pga.product(self.guard.to_dfa())

    def __str__(self):
        return f"observe({self.guard})"


class SequentialCompositionStatement(Statement):
    """The sequential composion `lhs;rhs`.
    """
    def __init__(self, lhs: Statement, rhs: Statement):
        self.lhs = lhs
        self.rhs = rhs

    def apply_semantics(self, pga: PGA) -> PGA:
        print(f"Calculating {str(self)}...")
        return self.rhs.apply_semantics(self.lhs.apply_semantics(pga))

    def __str__(self):
        return str(self.lhs) + ";" + str(self.rhs)

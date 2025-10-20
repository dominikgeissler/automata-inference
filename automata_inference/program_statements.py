from __future__ import annotations
from abc import ABC, abstractmethod

from symengine import Rational

from automata_inference.guards import (
    Guard,
    LtGuard,
    ModGuard,
    LandGuard,
    NegGuard,
    EqGuard,
    GtGuard,
    LeqGuard,
    GeqGuard,
)
from automata_inference.program_context import ProgramContext
from automata_inference.distributions import (
    Distribution,
    DiracDistribution,
    BernoulliDistribution,
    GeometricDistribution,
    NegBinomialDistribution,
    UniformDistribution,
)
from automata_inference.automata_factory import PGAFactory, DFAFactory, PGA

CONSTANT_KEY = "1"


class Statement(ABC):
    """Represents a program statement."""

    @abstractmethod
    def apply_semantics(self, pga: PGA, context: ProgramContext) -> PGA:
        """Computes the semantics of the program statement.

        Args:
            pga (PGA): The input PGA.

        Returns:
            PGA: The result of the semantics.
        """


# Todo one assignment statement?
class SkipStatement(Statement):
    """Effectless program."""

    def __init__(self):
        pass

    def apply_semantics(self, pga, context) -> PGA:
        return pga

    def __str__(self):
        return "skip"


class SetToZeroStatement(Statement):
    """The set to zero statement `indeterminate := 0`."""

    def __init__(self, indeterminate):
        self.indeterminate = indeterminate

    def apply_semantics(self, pga, context) -> PGA:
        print(f"Calculating {str(self)}...")
        return pga.substitute(self.indeterminate, 1, context)

    def __str__(self):
        return f"{self.indeterminate} := 0"


class IncrementConstantStatement(Statement):
    """The increment constant statement `indeterminate += n`."""

    def __init__(self, indeterminate, n: int):
        self.indeterminate = indeterminate
        self.n = n

    # Special case -> Join?
    def apply_semantics(self, pga, context) -> PGA:
        print(f"Calculating {str(self)}...")
        return IncrementDistributionStatement(
            self.indeterminate, DiracDistribution(self.indeterminate, self.n)
        ).apply_semantics(pga, context)

    def __str__(self):
        return f"{self.indeterminate} += {self.n}"


class IncrementDistributionStatement(Statement):
    """The increment distribution statement `indeterminate += distribution`."""

    def __init__(self, indeterminate, distribution: Distribution):
        self.indeterminate = indeterminate
        self.distribution = distribution

    def apply_semantics(self, pga, context) -> PGA:
        print(f"Calculating {str(self)}...")
        return pga.concat(self.distribution.to_pga(context))

    def __str__(self):
        return f"{self.indeterminate} += {self.distribution}"


class IncrementVariableStatement(Statement):
    """The increment variable statement `indeterminate_lhs += indeterminate_rhs`."""

    def __init__(self, indeterminate_lhs, indeterminate_rhs):
        self.indeterminate_lhs = indeterminate_lhs
        self.indeterminate_rhs = indeterminate_rhs

    # Special case -> Join?
    def apply_semantics(self, pga, context) -> PGA:
        print(f"Calculating {str(self)}...")
        return IidSamplingStatement(
            self.indeterminate_lhs,
            DiracDistribution(self.indeterminate_lhs, 1),
            self.indeterminate_rhs,
        ).apply_semantics(pga, context)

    def __str__(self):
        return f"{self.indeterminate_lhs} += {self.indeterminate_rhs}"


class IidSamplingStatement(Statement):
    """The iid statement `indeterminate_lhs += iid(distribution, indeterminate_rhs)`."""

    def __init__(self, indeterminate_lhs, distribution: Distribution, indeterminate_rhs):
        self.indeterminate_lhs = indeterminate_lhs
        self.distribution = distribution
        self.indeterminate_rhs = indeterminate_rhs

    def apply_semantics(self, pga, context) -> PGA:
        print(f"Calculating {str(self)}...")
        return pga.transition_substitution(
            self.indeterminate_rhs,
            PGAFactory.dirac(self.indeterminate_rhs, 1, context.indeterminates).concat(
                self.distribution.to_pga(context)
            ),
        )

    def __str__(self):
        return f"{self.indeterminate_lhs} += iid({self.distribution}, {self.indeterminate_rhs})"


class CoinflipStatement(Statement):
    """The coinflip statement `{ lhs } [p] { rhs }`."""

    def __init__(self, lhs: Statement, p: Rational, rhs: Statement):
        assert 0 <= p <= 1, f"p has to be between 0 and 1, got {p=}"
        self.lhs = lhs
        self.p = p
        self.rhs = rhs

    def apply_semantics(self, pga, context) -> PGA:
        print(f"Calculating {str(self)}...")
        return self.lhs.apply_semantics(pga, context).weighted_union(
            self.rhs.apply_semantics(pga, context), self.p, 1 - self.p
        )

    def __str__(self):
        return f"{{ {self.lhs} }} [{self.p}] {{ {self.rhs} }}"


class IfStatement(Statement):
    """The if statement `if(guard) { then_statenent } else { else_statement }`."""

    def __init__(self, guard: Guard, then_statement: Statement, else_statement: Statement):
        self.guard = guard
        self.then_statement = then_statement
        self.else_statement = else_statement

    def apply_semantics(self, pga, context) -> PGA:
        print(f"Calculating {str(self)}...")
        guard_dfa = self.guard.to_dfa(context)
        neg_guard_dfa = DFAFactory.neg(guard_dfa)
        return self.then_statement.apply_semantics(pga.product(guard_dfa, context), context).weighted_union(
            self.else_statement.apply_semantics(pga.product(neg_guard_dfa, context), context), 1, 1
        )

    def __str__(self):
        return f"if({self.guard}) then {{ {self.then_statement} }} else {{ {self.else_statement} }}"


class MonusStatement(Statement):
    """The monus statement `indeterminate--`."""

    def __init__(self, indeterminate):
        self.indeterminate = indeterminate

    def apply_semantics(self, pga, context) -> PGA:
        return pga.decrement(self.indeterminate, context)

    def __str__(self):
        return f"{self.indeterminate}--"


class ObserveStatement(Statement):
    """The observe statement `observe(guard)`."""

    def __init__(self, guard: Guard):
        self.guard = guard

    def apply_semantics(self, pga, context) -> PGA:
        print(f"Calculating {str(self)}...")
        return pga.product(self.guard.to_dfa(context), context)

    def __str__(self):
        return f"observe({self.guard})"


class SequentialCompositionStatement(Statement):
    """The sequential composion `lhs;rhs`."""

    def __init__(self, lhs: Statement, rhs: Statement):
        self.lhs = lhs
        self.rhs = rhs

    def apply_semantics(self, pga, context) -> PGA:
        print(f"Calculating {str(self)}...")
        return self.rhs.apply_semantics(self.lhs.apply_semantics(pga, context), context)

    def __str__(self):
        return str(self.lhs) + ";" + str(self.rhs)


class Program:
    """Models a ReDiP program"""
    def __init__(self, body: Statement):
        self.body = body
        self.is_observe = check_observe(self.body)
        self.variables = get_variables_from_program(self.body)

    def apply_semantics(self, pga: PGA) -> PGA:
        """Calculates the semantics of the program given some distribution encoded as PGA.

        Args:
            pga (PGA): The input distribution.

        Returns:
            PGA: The posterior distribution.
        """
        return self.body.apply_semantics(pga, ProgramContext(indeterminates=self.variables | {CONSTANT_KEY}))

    def __str__(self):
        return str(self.body)


# === To be replaced by parsing ===


def check_observe(program: Statement) -> bool:
    """Checks whether a given program contains an observe-statement.

    Args:
        program (Statement): The program that should be checked.

    Returns:
        bool: Indicates whether the program contains an observe-statement.
    """
    if isinstance(program, ObserveStatement):
        return True
    if isinstance(program, (SequentialCompositionStatement | CoinflipStatement)):
        return check_observe(program.lhs) or check_observe(program.rhs)
    if isinstance(program, IfStatement):
        return check_observe(program.then_statement) or check_observe(program.else_statement)
    return False


def get_variables_from_program(program: Statement) -> set[str]:
    """Collects the variables from a given program.

    Args:
        program (Statement): The program the variables should be collected from.

    Returns:
        set[str]: The set of variables contained in the program.
    """
    if isinstance(program, ObserveStatement):
        return get_variables_from_guard(program.guard)
    if isinstance(program, IfStatement):
        return (
            get_variables_from_guard(program.guard)
            | get_variables_from_program(program.then_statement)
            | get_variables_from_program(program.else_statement)
        )
    if isinstance(program, (SequentialCompositionStatement | CoinflipStatement)):
        return get_variables_from_program(program.lhs) | get_variables_from_program(program.rhs)
    if isinstance(program, IncrementVariableStatement):
        return {program.indeterminate_lhs, program.indeterminate_rhs}
    if isinstance(program, IidSamplingStatement):
        return {program.indeterminate_lhs, program.indeterminate_rhs} | get_variables_from_distribution(
            program.distribution
        )
    if isinstance(program, IncrementDistributionStatement):
        return {program.indeterminate} | get_variables_from_distribution(program.distribution)
    if isinstance(program, (SetToZeroStatement | IncrementConstantStatement | MonusStatement)):
        return {program.indeterminate}
    return set()


def get_variables_from_distribution(distr: Distribution) -> set[str]:
    """Collects the variable from a distribution.

    Args:
        distr (Distribution): The distribution the variable should be collected from.

    Returns:
        set[str]: The set of variables included in the distribution.
    """
    if isinstance(
        distr,
        (
            BernoulliDistribution
            | DiracDistribution
            | GeometricDistribution
            | NegBinomialDistribution
            | UniformDistribution
        ),
    ):
        return {distr.indeterminate}
    return set()


def get_variables_from_guard(guard: Guard) -> set[str]:
    """Collects the variables from a given guard.

    Args:
        guard (Guard): The guard the variables should be extracted from.

    Returns:
        set[str]: The set of variables included in the guard. 
    """
    if isinstance(guard, LandGuard):
        return get_variables_from_guard(guard.guard1) | get_variables_from_guard(guard.guard2)
    if isinstance(guard, NegGuard):
        return get_variables_from_guard(guard.guard)
    if isinstance(guard, (LtGuard | ModGuard | EqGuard | GtGuard | LeqGuard | GeqGuard)):
        return {guard.indeterminate}
    return set()


# ================================

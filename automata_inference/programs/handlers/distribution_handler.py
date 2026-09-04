from automata_inference.parser.ast.distributions import (
    Distribution,
    Dirac,
    Bernoulli,
    NegBinom,
    Uniform,
    Geometric,
)
from automata_inference.automata.model import PGA
from automata_inference.automata.factory import PGAFactory


class DistributionHandler:

    @staticmethod
    def compile(distribution: Distribution, indeterminate: str) -> PGA:
        if isinstance(distribution, Dirac):
            return PGAFactory.dirac(indeterminate, distribution.n)
        if isinstance(distribution, Geometric):
            return PGAFactory.geometric(indeterminate, distribution.p)
        if isinstance(distribution, Bernoulli):
            return PGAFactory.bernoulli(indeterminate, distribution.p)
        if isinstance(distribution, Uniform):
            return PGAFactory.uniform(indeterminate, distribution.n)
        if isinstance(distribution, NegBinom):
            return PGAFactory.neg_binomial(
                indeterminate, distribution.n, distribution.p
            )

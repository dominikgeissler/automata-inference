from abc import abstractmethod, ABC

from symengine import Rational

from automata_inference.automata_factory import PGAFactory, PGA

from automata_inference.program_context import ProgramContext


class Distribution(ABC):
    """Models the abstract distribution."""

    @abstractmethod
    def to_pga(self, context: ProgramContext) -> PGA:
        """Transforms a distribution to the corresponding PGA.

        Returns:
            PGA: The PGA which encodes the distribution
        """


class BernoulliDistribution(Distribution):
    """
    Represents the bernoulli distribution.
    """

    def __init__(self, indeterminate: str, p: Rational):
        assert 0 <= p <= 1, f"p has to be between 0 and 1, got {p=}"
        self.indeterminate = indeterminate
        self.p = p

    def to_pga(self, context) -> PGA:
        return PGAFactory.bernoulli(self.indeterminate, self.p, context.indeterminates)

    def __str__(self):
        return f"Binom({self.p})"


class NegBinomialDistribution(Distribution):
    """Represents the negative binomial distribution."""

    def __init__(self, indeterminate: str, n: int, p: Rational):
        assert n > 0, f"n has to be greater than 0, got {n=}"
        assert 0 <= p <= 1, f"p has to be between 0 and 1, got {p=}"
        self.indeterminate = indeterminate
        self.n = n
        self.p = p

    def to_pga(self, context) -> PGA:
        return PGAFactory.neg_binomial(self.indeterminate, self.n, self.p, context.indeterminates)

    def __str__(self):
        return f"NegBinom({self.n}, {self.p})"


class GeometricDistribution(Distribution):
    """Represents the geometric distribution."""

    def __init__(self, indeterminate: str, p: Rational):
        assert 0 <= p <= 1, f"p has to be between 0 and 1, got {p=}"
        self.indeterminate = indeterminate
        self.p = p

    def to_pga(self, context) -> PGA:
        return PGAFactory.geometric(self.indeterminate, self.p, context.indeterminates)

    def __str__(self):
        return f"Geom({self.p})"


class UniformDistribution(Distribution):
    """Represents the uniform distribution."""

    def __init__(self, indeterminate: str, n: int):
        assert n > 0, f"n has to be greater than 0, got {n=}"
        self.indeterminate = indeterminate
        self.n = n

    def to_pga(self, context) -> PGA:
        return PGAFactory.uniform(self.indeterminate, self.n, context.indeterminates)

    def __str__(self):
        return f"Unif({self.n})"


class DiracDistribution(Distribution):
    """Represents the dirac distribution."""

    def __init__(self, indeterminate: str, n: int):
        assert n >= 0, f"n has to be at least 0, got {n=}"
        self.indeterminate = indeterminate
        self.n = n

    def to_pga(self, context) -> PGA:
        return PGAFactory.dirac(self.indeterminate, self.n, context.indeterminates)

    def __str__(self):
        return f"Dirac({self.n})"

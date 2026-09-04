from automata_inference.automata.factory import PGAFactory
from automata_inference.automata.model import PGA
from automata_inference.parser.ast.distributions import (
    Bernoulli,
    Dirac,
    Distribution,
    Geometric,
    NegBinom,
    Uniform,
)


class DistributionHandler:
    """Handles the compilation of parsed distributions into PGA representations."""
    

    @staticmethod
    def compile(distribution: Distribution, indeterminate: str) -> PGA:
        """Handles the compilation of parsed distributions into PGA representations.

        Args:
            distribution (Distribution): The parsed distribution to be compiled. 
            indeterminate (str): The indeterminate associated with the distribution.
            
        Raises:
                ValueError: If the distribution type is unsupported.
        
        Returns:
                PGA: The PGA representation of the distribution.
        """
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
        raise ValueError(f"Unsupported distribution type: {type(distribution)}")
from automaton import PGA
from automata_factory import PGAFactory
from abc import abstractmethod, ABC

class Distribution(ABC):
    @abstractmethod
    def to_pga(self) -> PGA:
        pass
    
class BernoulliDistribution(Distribution):
    """
        Represents the bernoulli distribution.
    """
    def __init__(self, indeterminate, p: float):
        assert 0 <= p and p <= 1, f"p has to be between 0 and 1, got {p=}"
        self.indeterminate = indeterminate
        self.p = p
        
    def to_pga(self) -> PGA:
        return PGAFactory.bernoulli(self.indeterminate, self.p)
    
    def __str__(self):
        return f"Binom({self.p})"

class NegBinomialDistribution(Distribution):
    def __init__(self, indeterminate, n: int, p: float):
        assert n > 0, f"n has to be greater than 0, got {n=}"
        assert 0 <= p and p <= 1, f"p has to be between 0 and 1, got {p=}"
        self.indeterminate = indeterminate
        self.n = n
        self.p = p
        
    def to_pga(self) -> PGA:
        return PGAFactory.neg_binomial(self.indeterminate, self.n, self.p)
    
    def __str__(self):
        return f"NegBinom({self.n}, {self.p})"

class GeometricDistribution(Distribution):
    def __init__(self, indeterminate, p: float):
        assert 0 <= p and p <= 1, f"p has to be between 0 and 1, got {p=}"
        self.indeterminate = indeterminate
        self.p = p
        
    def to_pga(self) -> PGA:
        return PGAFactory.geometric(self.indeterminate, self.p)
    
    def __str__(self):
        return f"Geom({self.p})"

class UniformDistribution(Distribution):
    def __init__(self, indeterminate, n: int):
        assert n > 0, f"n has to be greater than 0, got {n=}"
        self.indeterminate = indeterminate
        self.n = n
        
    def to_pga(self) -> PGA:
        return PGAFactory.uniform(self.indeterminate, self.n)
    
    def __str__(self):
        return f"Unif({self.n})"

class DiracDistribution(Distribution):
    def __init__(self, indeterminate, n: int):
        assert n >= 0, f"n has to be at least 0, got {n=}"
        self.indeterminate = indeterminate
        self.n = n
        
    def to_pga(self) -> PGA:
        return PGAFactory.dirac(self.indeterminate, self.n)
    
    def __str__(self):
        return f"Dirac({self.n})"

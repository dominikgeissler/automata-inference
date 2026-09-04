from dataclasses import dataclass

from automata_inference.parser.ast.guards import Guard

class Query:
    """Base class""" 
    
@dataclass(frozen=True)
class PosteriorProbability(Query):
    guard: Guard
    
@dataclass(frozen=True)
class UnivariateMoment(Query):
    variable: str
    moment: int
    
@dataclass(frozen=True)
class MixedMoment(Query):
    variable1: str
    variable2: str

    
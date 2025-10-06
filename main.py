from program_statements import *
from distributions import *
from guards import *
from automata_factory import *

# X += Geom(0.5); observe(X < 3)
program = SequentialCompositionStatement(
    lhs=IncrementDistributionStatement("X", GeometricDistribution("X", 0.5)),
    rhs=ObserveStatement(
        LtGuard("X", 3)
    )
)

print(program)
input_pga = PGAFactory.one()
print(input_pga)
print(program.apply_semantics(input_pga))
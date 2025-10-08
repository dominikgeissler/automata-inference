from program_statements import *
from distributions import *
from guards import *
from automata_factory import *
from visualizer import visualize

# X += Geom(0.5); observe(X < 3)
program = SequentialCompositionStatement(
    lhs=IncrementDistributionStatement("X", GeometricDistribution("X", 0.5)),
    rhs=ObserveStatement(
        LtGuard("X", 10)
    )
)

# program = CoinflipStatement(
#     lhs=IncrementConstantStatement("X", 1),
#     p=0.5,
#     rhs=IncrementConstantStatement("X", 3)
# )

# program = IidSamplingStatement("X", GeometricDistribution("X", 0.5), "Y")


print(program)
input_pga = PGAFactory.geometric("Y", 0.5)
print(input_pga)
out = program.apply_semantics(input_pga)

visualize(out, view=True)
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


program = SequentialCompositionStatement(
    lhs=CoinflipStatement(
        lhs=SetToZeroStatement("Y"),
        p=0.9,
        rhs=SequentialCompositionStatement(
            lhs=SetToZeroStatement("Y"),
            rhs=IncrementConstantStatement("Y", 1)
        )
    ),
    rhs=SequentialCompositionStatement(
        lhs=IfStatement(
            guard=EqGuard("Y", 0),
            then_statement=IncrementDistributionStatement("X", NegBinomialDistribution("X", 1, 0.5)),
            else_statement=IncrementDistributionStatement("X", NegBinomialDistribution("X", 2, 0.5))
        ),
        rhs=ObserveStatement(guard=NegGuard(LtGuard("X", 2)))
    )
)

print(program)
input_pga = PGAFactory.one()
out = program.apply_semantics(input_pga)
from minimization import minimize

minimize(out)
visualize(out, view=True)
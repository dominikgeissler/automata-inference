from program_statements import (
    SequentialCompositionStatement,
    IncrementConstantStatement,
    ObserveStatement,
    IfStatement,
    SetToZeroStatement,
    CoinflipStatement,
    IncrementDistributionStatement,
    MonusStatement
)
from distributions import GeometricDistribution, NegBinomialDistribution
from guards import LtGuard, EqGuard, GeqGuard
from automata_factory import PGAFactory, minimize
from visualizer import visualize

# todo symbolic fractions

# X += Geom(0.5); observe(X < 3)
program = SequentialCompositionStatement(
    lhs=IncrementDistributionStatement("X", GeometricDistribution("X", 0.5)),
    rhs=ObserveStatement(LtGuard("X", 10)),
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
            lhs=SetToZeroStatement("Y"), rhs=IncrementConstantStatement("Y", 1)
        ),
    ),
    rhs=SequentialCompositionStatement(
        lhs=IfStatement(
            guard=EqGuard("Y", 0),
            then_statement=IncrementDistributionStatement(
                "X", NegBinomialDistribution("X", 1, 0.5)
            ),
            else_statement=IncrementDistributionStatement(
                "X", NegBinomialDistribution("X", 2, 0.5)
            ),
        ),
        rhs=ObserveStatement(guard=GeqGuard("X", 2)),
    ),
)

program = MonusStatement("X")

print(program)
input_pga = PGAFactory.geometric("X", 0.5)
out = program.apply_semantics(input_pga)

minimize(out)
visualize(out, view=True)

from automata_factory import PGAFactory
from visualizer import visualize
from program_statements import (
    SequentialCompositionStatement,
    CoinflipStatement,
    SetToZeroStatement,
    IncrementConstantStatement,
    IfStatement,
    IncrementDistributionStatement,
    ObserveStatement,
)
from guards import EqGuard, GeqGuard
from distributions import NegBinomialDistribution

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
print(program)

input_pga = PGAFactory.one()
out = program.apply_semantics(input_pga)
visualize(out, view=True)

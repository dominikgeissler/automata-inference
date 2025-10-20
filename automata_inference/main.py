import time
from symengine import Rational
from automata_inference.automata_factory import PGAFactory
from automata_inference.visualizer import visualize
from automata_inference.program_statements import (
    SequentialCompositionStatement,
    CoinflipStatement,
    SetToZeroStatement,
    IncrementConstantStatement,
    IfStatement,
    IncrementDistributionStatement,
    ObserveStatement,
    Program,
)
from automata_inference.guards import EqGuard, GeqGuard
from automata_inference.distributions import NegBinomialDistribution

program = Program(
    SequentialCompositionStatement(
        lhs=CoinflipStatement(
            lhs=SetToZeroStatement("R"),
            p=Rational(9, 10),
            rhs=SequentialCompositionStatement(lhs=SetToZeroStatement("R"), rhs=IncrementConstantStatement("R", 1)),
        ),
        rhs=SequentialCompositionStatement(
            lhs=IfStatement(
                guard=EqGuard("R", 0),
                then_statement=IncrementDistributionStatement("X", NegBinomialDistribution("X", 1, Rational(1, 2))),
                else_statement=IncrementDistributionStatement("X", NegBinomialDistribution("X", 2, Rational(1, 2))),
            ),
            rhs=ObserveStatement(guard=GeqGuard("X", 2)),
        ),
    )
)

print(program.variables)
print(program)
input_pga = PGAFactory.one((program.variables | {"1"}))
start = time.time()
out = program.apply_semantics(input_pga)
print(f"Duration: {time.time() - start}")
visualize(out, "bla", view=True)

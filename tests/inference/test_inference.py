from automata_inference.automata_factory import PGA, PGAFactory
from automata_inference.program_statements import (
    SequentialCompositionStatement,
    CoinflipStatement,
    SetToZeroStatement,
    IncrementConstantStatement,
    IfStatement,
    IncrementDistributionStatement,
    ObserveStatement,
)
from automata_inference.guards import EqGuard, GeqGuard
from automata_inference.distributions import NegBinomialDistribution
# TODO this is a very bad test but convenient to see whether something breaks


def test_ictac_example():
    expected = PGA(
        {
            "(q_0_1_1,p_1)",
            "(q_0_1,p_2)",
            "((q_1_1_1,p_1)_1,p_0)",
            "((q_0_1,p_0)_1,p_0)",
            "(q_0,p_0)",
            "(q_0_1_1,p_2)",
            "(q_0,p_2)",
            "((q_0,p_0),p_0)",
            "(q_0,p_1)",
            "(q_0_1_1,p_0)",
            "((q_0_1_1,p_0)_1,p_0)",
            "(q_0_1,p_0)",
            "(q_0_1,p_1)",
        },
        {
            "X": [
                (0.5, "(q_0,p_0)", "(q_0,p_1)"),
                (0.5, "(q_0,p_1)", "(q_0,p_2)"),
                (0.5, "(q_0,p_2)", "(q_0,p_2)"),
                (0.5, "(q_0_1,p_0)", "(q_0_1,p_1)"),
                (0.5, "(q_0_1,p_1)", "(q_0_1,p_2)"),
                (0.5, "(q_0_1,p_2)", "(q_0_1,p_2)"),
                (0.5, "(q_0_1_1,p_0)", "(q_0_1_1,p_1)"),
                (0.5, "(q_0_1_1,p_1)", "(q_0_1_1,p_2)"),
                (0.5, "(q_0_1_1,p_2)", "(q_0_1_1,p_2)"),
            ],
            "Y": [(1.0, "((q_0_1_1,p_0)_1,p_0)", "((q_1_1_1,p_1)_1,p_0)")],
            "Z": [],
            "1": [
                (1, "((q_0,p_0),p_0)", "(q_0,p_0)"),
                (1, "((q_0_1,p_0)_1,p_0)", "((q_0_1_1,p_0)_1,p_0)"),
                (0.5, "(q_0_1,p_2)", "(q_0_1_1,p_2)"),
                (0.5, "(q_0_1,p_1)", "(q_0_1_1,p_1)"),
                (0.5, "(q_0_1,p_0)", "(q_0_1_1,p_0)"),
                (1, "((q_1_1_1,p_1)_1,p_0)", "(q_0_1,p_0)")
            ],
        },
        {(0.09999999999999998, "((q_0_1,p_0)_1,p_0)"), (0.9, "((q_0,p_0),p_0)")},
        {(0.5, "(q_0_1_1,p_2)"), (0.5, "(q_0,p_2)")},
    )
    program = SequentialCompositionStatement(
        lhs=CoinflipStatement(
            lhs=SetToZeroStatement("Y"),
            p=0.9,
            rhs=SequentialCompositionStatement(lhs=SetToZeroStatement("Y"), rhs=IncrementConstantStatement("Y", 1)),
        ),
        rhs=SequentialCompositionStatement(
            lhs=IfStatement(
                guard=EqGuard("Y", 0),
                then_statement=IncrementDistributionStatement("X", NegBinomialDistribution("X", 1, 0.5)),
                else_statement=IncrementDistributionStatement("X", NegBinomialDistribution("X", 2, 0.5)),
            ),
            rhs=ObserveStatement(guard=GeqGuard("X", 2)),
        ),
    )

    input_pga = PGAFactory.one()
    result = program.apply_semantics(input_pga)
    assert result.states == expected.states
    assert result.final == expected.final
    assert result.initial == expected.initial
    for indeterminate, transitions in result.transition_matrix.items():
        for trans in transitions:
            assert trans in expected.transition_matrix[indeterminate], f"{trans} not included"

    for indeterminate, transitions in expected.transition_matrix.items():
        for trans in transitions:
            assert trans in result.transition_matrix[indeterminate], f"{trans} not included"

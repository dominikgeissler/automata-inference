from symengine import Rational

from automata_inference.automata_factory import PGA, PGAFactory
from automata_inference.program_statements import (
    SequentialCompositionStatement,
    CoinflipStatement,
    AssignStatement,
    IncrementStatement,
    IfStatement,
    ObserveStatement,
    Program,
)
from automata_inference.guards import EqGuard, NegGuard, LtGuard
from automata_inference.distributions import NegBinomialDistribution

from tests.utils import compare_dicts_with_unordered_lists

import pytest
# this is a very bad test but convenient to see whether something breaks


# TODO fix this test (account for normalization)
@pytest.mark.skip(reason="Fix this")
def test_ictac_example():
    """Runs the ICTAC example and checks whether the result matches the expected one."""
    expected = PGA(
        {
            "(q_0,p_0)",
            "(q_0_1_1,p_0)",
            "(q_0_1_1,p_2)",
            "(q_0,p_1)",
            "(q_0_1,p_2)",
            "(q_0_1_1,p_1)",
            "(q_0_1,p_1)",
            "((q_0_1_1_,p_0)_1,p_0)",
            "((q_0_1_,p_0)_1,p_0)",
            "((q_0_1__1_,p_0)_1,p_0)",
            "(q_0_1,p_0)",
            "((q_1_1__1_,p_1)_1,p_0)",
            "(q_0,p_2)",
            "((q_0,p_0),p_0)",
            "((q_0_1,p_0),p_0)",
        },
        {
            "1": [
                (1, "((q_0,p_0),p_0)", "((q_0_1,p_0),p_0)"),
                (1, "((q_0_1,p_0),p_0)", "(q_0,p_0)"),
                (1, "((q_0_1_,p_0)_1,p_0)", "((q_0_1_1_,p_0)_1,p_0)"),
                (1, "((q_0_1_1_,p_0)_1,p_0)", "((q_0_1__1_,p_0)_1,p_0)"),
                (Rational(1,2), "(q_0_1,p_1)", "(q_0_1_1,p_1)"),
                (Rational(1,2), "(q_0_1,p_2)", "(q_0_1_1,p_2)"),
                (Rational(1,2), "(q_0_1,p_0)", "(q_0_1_1,p_0)"),
                (1, "((q_1_1__1_,p_1)_1,p_0)", "(q_0_1,p_0)"),
            ],
            "X": [
                (Rational(1,2), "(q_0,p_0)", "(q_0,p_1)"),
                (Rational(1,2), "(q_0,p_1)", "(q_0,p_2)"),
                (Rational(1,2), "(q_0,p_2)", "(q_0,p_2)"),
                (Rational(1,2), "(q_0_1,p_0)", "(q_0_1,p_1)"),
                (Rational(1,2), "(q_0_1,p_1)", "(q_0_1,p_2)"),
                (Rational(1,2), "(q_0_1,p_2)", "(q_0_1,p_2)"),
                (Rational(1,2), "(q_0_1_1,p_0)", "(q_0_1_1,p_1)"),
                (Rational(1,2), "(q_0_1_1,p_1)", "(q_0_1_1,p_2)"),
                (Rational(1,2), "(q_0_1_1,p_2)", "(q_0_1_1,p_2)"),
            ],
            "R": [(1, "((q_0_1__1_,p_0)_1,p_0)", "((q_1_1__1_,p_1)_1,p_0)")],
        },
        {(Rational(1,10), "((q_0_1_,p_0)_1,p_0)"), (Rational(9,10), "((q_0,p_0),p_0)")},
        {(Rational(1,2), "(q_0,p_2)"), (Rational(1,2), "(q_0_1_1,p_2)")},
    )
    program = Program(
        SequentialCompositionStatement(
            lhs=CoinflipStatement(
                lhs=AssignStatement("R", 0),
                p=Rational(9, 10),
                rhs=SequentialCompositionStatement(lhs=AssignStatement("R", 0), rhs=IncrementStatement("R", 1)),
            ),
            rhs=SequentialCompositionStatement(
                lhs=IfStatement(
                    guard=EqGuard("R", 0),
                    then_statement=IncrementStatement("X", NegBinomialDistribution("X", 1, Rational(1, 2))),
                    else_statement=IncrementStatement("X", NegBinomialDistribution("X", 2, Rational(1, 2))),
                ),
                rhs=ObserveStatement(guard=NegGuard(LtGuard("X", 2))),
            ),
        ),
        True,
        {"X", "R"},
    )
    input_pga = PGAFactory.one(program.variables | {"1"})
    actual = program.apply_semantics(input_pga)
    print(actual)
    assert expected.states == actual.states, f"States do not match, expected {expected.states}, got {actual.states}"
    assert expected.initial == actual.initial, (
        f"Initial states do not match, expected {expected.initial}, got {actual.initial}"
    )
    assert expected.final == actual.final, f"Final states do not match, expected {expected.final}, got {actual.final}"
    assert compare_dicts_with_unordered_lists(expected.transition_matrix, actual.transition_matrix), (
        f"Transition matrices do not match, expected {expected.transition_matrix}, got {actual.transition_matrix}"
    )

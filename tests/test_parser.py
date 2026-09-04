import pytest
from symengine import Rational

from automata_inference.parser.parser import parse_string
from automata_inference.parser.ast.distributions import (
    Bernoulli,
    Dirac,
    Geometric,
    NegBinom,
    Uniform,
)
from automata_inference.parser.ast.guards import (
    And,
    Equals,
    Implies,
    LessThan,
    ModuloEquals,
    Not,
    Or,
)
from automata_inference.parser.ast.queries import (
    MixedMoment,
    PosteriorProbability,
    UnivariateMoment,
)
from automata_inference.parser.ast.statements import (
    AssignStatement,
    CoinflipStatement,
    ConstantRhs,
    DistributionRhs,
    IidRhs,
    IfStatement,
    IncrementStatement,
    MonusStatement,
    ObserveStatement,
    SequentialCompositionStatement,
    SkipStatement,
    VariableRhs,
)


def test_parser_undefined_variables():
    program = """
    var X;
    
    R := Geom(1/2)
    """
    with pytest.raises(ValueError, match="Variable R not defined."):
        parse_string(program)


def test_parser_division_by_zero():
    program = """
    var X;
    { X := 1} [1/0] {X := 0}
    """

    with pytest.raises(ValueError, match="Division by 0."):
        parse_string(program)


def test_parser_empty_program():
    parsed = parse_string("var X;")

    assert parsed.body is None
    assert parsed.variables == frozenset({"X"})
    assert parsed.query is None
    assert not parsed.is_observe


def test_parser_rhs_variants():
    parsed = parse_string("""
        var X;
        var Y;
        
        X := 3;
        X += Y;
        Y := iid(Bern(1/2), X);
        X += Unif(4);
        """)

    assert parsed.body == SequentialCompositionStatement(
        left=AssignStatement(variable="X", rhs=ConstantRhs(value=3)),
        right=SequentialCompositionStatement(
            left=IncrementStatement(variable="X", rhs=VariableRhs(variable="Y")),
            right=SequentialCompositionStatement(
                left=AssignStatement(
                    variable="Y",
                    rhs=IidRhs(distribution=Bernoulli(p=Rational(1, 2)), variable="X"),
                ),
                right=IncrementStatement(
                    variable="X", rhs=DistributionRhs(distribution=Uniform(n=4))
                ),
            ),
        ),
    )


def test_parser_all_distribution_variants():
    parsed = parse_string("""
        var X;
        X := Geom(1/3);
        X += NegBinom(2, 1/4);
        X := Bern(2/5);
        X += Dirac(3);
        """)

    assert parsed.body == SequentialCompositionStatement(
        left=AssignStatement(
            variable="X", rhs=DistributionRhs(Geometric(p=Rational(1, 3)))
        ),
        right=SequentialCompositionStatement(
            left=IncrementStatement(
                variable="X",
                rhs=DistributionRhs(distribution=NegBinom(n=2, p=Rational(1, 4))),
            ),
            right=SequentialCompositionStatement(
                left=AssignStatement(
                    variable="X",
                    rhs=DistributionRhs(distribution=Bernoulli(p=Rational(2, 5))),
                ),
                right=IncrementStatement(
                    variable="X", rhs=DistributionRhs(distribution=Dirac(n=3))
                ),
            ),
        ),
    )


def test_parser_statement_forms():
    parsed = parse_string("""
        var X;
        skip;
        X--;
        { skip } [1/4] { X := 1 };
        if (X < 2) { X := 1 } else { X := 0 };
        observe(X = 1);
        """)

    assert parsed.is_observe
    assert parsed.body == SequentialCompositionStatement(
        left=SkipStatement(),
        right=SequentialCompositionStatement(
            left=MonusStatement(variable="X"),
            right=SequentialCompositionStatement(
                left=CoinflipStatement(
                    left=SkipStatement(),
                    p=Rational(1, 4),
                    right=AssignStatement(variable="X", rhs=ConstantRhs(1)),
                ),
                right=SequentialCompositionStatement(
                    left=IfStatement(
                        guard=LessThan(variable="X", value=2),
                        then_statement=AssignStatement(
                            variable="X", rhs=ConstantRhs(1)
                        ),
                        else_statement=AssignStatement(
                            variable="X", rhs=ConstantRhs(0)
                        ),
                    ),
                    right=ObserveStatement(guard=Equals(variable="X", value=1)),
                ),
            ),
        ),
    )


@pytest.mark.skip(
    "This should work after adjusting the grammar to handle guards better."
)
def test_parser_guard_composition_uses_both_operands():
    parsed = parse_string("""
        var X;
        var Y;
        observe(!(X < 1 || Y = 2) && X % 3 = 1);
        """)

    assert parsed.body == ObserveStatement(
        And(
            Not(Or(LessThan("X", 1), Equals("Y", 2))),
            ModuloEquals("X", 3, 1),
        )
    )


def test_parser_implication_guard():
    parsed = parse_string("""
        var X;
        var Y;
        observe(X < 1 -> Y = 2);
        """)

    assert parsed.body == ObserveStatement(Implies(LessThan("X", 1), Equals("Y", 2)))


def test_parser_query_variants():
    assert parse_string("var X; ?Pr[X < 2]").query == PosteriorProbability(
        LessThan("X", 2)
    )
    assert parse_string("var X; ?E[X, 2]").query == UnivariateMoment("X", 2)
    assert parse_string("var X; var Y; ?E[X, Y]").query == MixedMoment("X", "Y")


def test_parser_while_is_not_supported():
    with pytest.raises(NotImplementedError, match="While currently not supported"):
        parse_string("var X; while (X < 1) { X += 1 }")

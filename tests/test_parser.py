from pytest import raises
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
    with raises(ValueError, match="Variable R not defined."):
        parse_string(program)
    
    
def test_parser_division_by_zero():
    program = """
    var X;
    { X := 1} [1/0] {X := 0}
    """
    
    with raises(ValueError, match="Division by 0."):
        parse_string(program)


def test_parser_empty_program():
    parsed = parse_string("var X;")

    assert parsed.body is None
    assert parsed.variables == frozenset({"X"})
    assert parsed.query is None
    assert not parsed.is_observe


def test_parser_increment():
    parsed = parse_string(
        """
        var X;
        var Y;
        
        X += Y;
        """        
    )
    print(parsed)
    assert False

def test_parser_rhs_variants():
    parsed = parse_string(
        """
        var X;
        var Y;
        
        X := 3;
        X += Y;
        Y := iid(Bern(1/2), X);
        X += Unif(4);
        """
    )

    assert parsed.body == SequentialCompositionStatement(
        left=SequentialCompositionStatement(
            left=SequentialCompositionStatement(
                left=AssignStatement("X", ConstantRhs(3)),
                right=IncrementStatement("X", VariableRhs("Y")),
            ),
            right=AssignStatement("Y", IidRhs(Bernoulli(Rational(1, 2)), "X")),
        ),
        right=IncrementStatement("X", DistributionRhs(Uniform(4))),
    )


def test_parser_all_distribution_variants():
    parsed = parse_string(
        """
        var X;
        X := Geom(1/3);
        X += NegBinom(2, 1/4);
        X := Bern(2/5);
        X += Dirac(3);
        """
    )

    assert parsed.body == SequentialCompositionStatement(
        left=SequentialCompositionStatement(
            left=SequentialCompositionStatement(
                left=AssignStatement("X", DistributionRhs(Geometric(Rational(1, 3)))),
                right=IncrementStatement("X", DistributionRhs(NegBinom(2, Rational(1, 4)))),
            ),
            right=AssignStatement("X", DistributionRhs(Bernoulli(Rational(2, 5)))),
        ),
        right=IncrementStatement("X", DistributionRhs(Dirac(3))),
    )


def test_parser_statement_forms():
    parsed = parse_string(
        """
        var X;
        skip;
        X--;
        { skip } [1/4] { X := 1 };
        if (X < 2) { X := 1 } else { X := 0 };
        observe(X = 1);
        """
    )

    assert parsed.is_observe
    assert isinstance(parsed.body, SequentialCompositionStatement)
    assert parsed.body.left == SequentialCompositionStatement(
        left=SequentialCompositionStatement(
            left=SequentialCompositionStatement(
                left=SkipStatement(),
                right=MonusStatement("X"),
            ),
            right=CoinflipStatement(
                left=SkipStatement(),
                p=Rational(1, 4),
                right=AssignStatement("X", ConstantRhs(1)),
            ),
        ),
        right=IfStatement(
            guard=LessThan("X", 2),
            then_statement=AssignStatement("X", ConstantRhs(1)),
            else_statement=AssignStatement("X", ConstantRhs(0)),
        ),
    )
    assert parsed.body.right == ObserveStatement(Equals("X", 1))


def test_parser_guard_composition_uses_both_operands():
    parsed = parse_string(
        """
        var X;
        var Y;
        observe(!(X < 1 || Y = 2) && X % 3 = 1);
        """
    )

    assert parsed.body == ObserveStatement(
        And(
            Not(Or(LessThan("X", 1), Equals("Y", 2))),
            ModuloEquals("X", 3, 1),
        )
    )


def test_parser_implication_guard():
    parsed = parse_string(
        """
        var X;
        var Y;
        observe(X < 1 -> Y = 2);
        """
    )

    assert parsed.body == ObserveStatement(
        Implies(LessThan("X", 1), Equals("Y", 2))
    )


def test_parser_query_variants():
    assert parse_string("var X; ?Pr[X < 2]").query == PosteriorProbability(
        LessThan("X", 2)
    )
    assert parse_string("var X; ?E[X, 2]").query == UnivariateMoment("X", 2)
    assert parse_string("var X; var Y; ?E[X, Y]").query == MixedMoment("X", "Y")


def test_parser_while_is_not_supported():
    with raises(NotImplementedError, match="While currently not supported"):
        parse_string("var X; while (X < 1) { X += 1 }")
    

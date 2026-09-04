from functools import reduce

from lark import Lark, Tree
from symengine import Rational

from automata_inference.parser.ast.distributions import (
    Bernoulli,
    Dirac,
    Distribution,
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
    Query,
    UnivariateMoment,
)
from automata_inference.parser.ast.statements import (
    AssignStatement,
    CoinflipStatement,
    ConstantRhs,
    DistributionRhs,
    IfStatement,
    IidRhs,
    IncrementStatement,
    MonusStatement,
    ObserveStatement,
    Program,
    Rhs,
    SequentialCompositionStatement,
    SkipStatement,
    Statement,
    VariableRhs,
)
from automata_inference.parser.grammar import get_grammar

# Heavily inspired by Philipp Schröers' work:
# https://github.com/Philipp15b/probably


def parse(program_path: str) -> Program:
    """Parses a program from a file.

    Args:
        program_path (str): The path to the program file.

    Returns:
        Program: The parsed program.
    """
    program = open(program_path, "r", encoding="utf-8").read()
    return parse_string(program)


def parse_string(program: str) -> Program:
    """Parses a program from a string.

    Args:
        program (str): The program code.

    Returns:
        Program: The parsed program.
    """
    parser = Lark(get_grammar(), start="program")
    ast = parser.parse(program)
    return _parse_tree(ast)


def _parse_tree(tree: Tree) -> Program:
    declarations = _parse_declarations(tree.children[0])
    variables = set(declarations)
    statements = _parse_statements(tree.children[1], variables)
    body = _statement_list_to_sequential_comp(statements) if statements else None
    if len(tree.children) > 2:
        query = _parse_query(tree.children[2], variables)
        return Program(
            body,
            any(isinstance(st, ObserveStatement) for st in statements),
            set(variables),
            query,
        )
    return Program(
        body,
        any(isinstance(st, ObserveStatement) for st in statements),
        set(variables),
    )


# === Declarations ===
def _parse_declarations(tree: Tree) -> list[str]:
    return [_parse_declaration(decl) for decl in tree.children]


def _parse_declaration(tree: Tree) -> str:
    return _parse_var(tree.children[0], set(), False)


# === Statements ===
def _parse_statements(tree: Tree, variables: set[str]):
    return [_parse_statement(t, variables) for t in tree.children]


def _parse_statement(tree: Tree, variables: set[str]):
    if tree.data == "skip":
        return SkipStatement()
    if tree.data == "assignment":
        return _parse_statement_assignment(tree, variables)
    if tree.data == "increment":
        return _parse_statement_increment(tree, variables)
    if tree.data == "monus":
        return _parse_statement_monus(tree, variables)
    if tree.data == "probchoice":
        return _parse_statement_probchoice(tree, variables)
    if tree.data == "if":
        return _parse_statement_if(tree, variables)
    if tree.data == "observe":
        return _parse_statement_observe(tree, variables)
    if tree.data == "while":
        return _parse_statement_while(tree, variables)
    raise ValueError(f"Statement not recognized, {tree.data}")


def _parse_statement_assignment(tree: Tree, variables: set[str]):
    indeterminate = _parse_var(tree.children[0], variables)
    rhs = _parse_rhs(tree.children[1], variables)
    return AssignStatement(indeterminate, rhs)


def _parse_statement_increment(tree: Tree, variables: set[str]):
    indeterminate = _parse_var(tree.children[0], variables)
    rhs = _parse_rhs(tree.children[1], variables)
    return IncrementStatement(indeterminate, rhs)


def _parse_statement_monus(tree: Tree, variables: set[str]):
    indeterminate = _parse_var(tree.children[0], variables)
    return MonusStatement(indeterminate)


def _parse_statement_probchoice(tree: Tree, variables: set[str]) -> CoinflipStatement:
    lhs = _statement_list_to_sequential_comp(
        _parse_statements(tree.children[0], variables)
    )
    p = _parse_frac(tree.children[1])
    rhs = _statement_list_to_sequential_comp(
        _parse_statements(tree.children[2], variables)
    )
    return CoinflipStatement(lhs, p, rhs)


def _parse_statement_if(tree: Tree, variables):
    guard = _parse_guard(tree.children[0].children[0], variables)
    then_statement = _statement_list_to_sequential_comp(
        _parse_statements(tree.children[1], variables)
    )
    if len(tree.children) > 2:
        else_statement = _statement_list_to_sequential_comp(
            _parse_statements(tree.children[2], variables)
        )
        return IfStatement(guard, then_statement, else_statement)
    return IfStatement(guard, then_statement)


def _parse_statement_observe(tree: Tree, variables: set[str]):
    guard = _parse_guard(tree.children[0].children[0], variables)
    return ObserveStatement(guard)


def _parse_statement_while(tree: Tree, variables: set[str]):
    raise NotImplementedError("While currently not supported :(")


def _parse_frac(tree: Tree) -> Rational:
    if int(str(tree.children[1])) == 0:
        raise ValueError("Division by 0.")
    return Rational(tree.children[0], tree.children[1])


def _parse_rhs(tree: Tree, variables: set[str]) -> Rhs:
    if tree.data == "const":
        return ConstantRhs(_parse_const(tree))
    if tree.data == "iid":
        distribution, variable = _parse_iid(tree, variables)
        return IidRhs(distribution, variable)
    if tree.data == "distribution":
        return DistributionRhs(_parse_distribution(tree.children[0]))
    if tree.data == "var":
        return VariableRhs(_parse_var(tree.children[0], variables))
    raise ValueError(f"Unknown rhs, {tree.data}")


def _parse_var(tree: Tree, variables: set[str], check_variables: bool = True) -> str:
    indeterminate = str(tree.children[0])
    if indeterminate not in variables and check_variables:
        raise ValueError(f"Variable {indeterminate} not defined.")
    return indeterminate


def _parse_const(tree: Tree) -> int:
    return _parse_int(tree.children[0])


def _parse_int(tree: Tree) -> int:
    return int(str(tree))


def _parse_iid(
    tree: Tree, variables: set[str]
) -> tuple[Distribution, str]:
    distribution = _parse_distribution(tree.children[0])
    indeterminate_rhs = _parse_var(tree.children[1], variables)
    return (distribution, indeterminate_rhs)


def _parse_distribution(tree: Tree) -> Distribution:
    if tree.data == "geometric":
        return _parse_distribution_geometric(tree)
    if tree.data == "uniform":
        return _parse_distribution_uniform(tree)
    if tree.data == "negbinom":
        return _parse_distribution_negbinom(tree)
    if tree.data == "bernoulli":
        return _parse_distribution_bernoulli(tree)
    if tree.data == "dirac":
        return _parse_distribution_dirac(tree)
    raise ValueError(f"Unknown distribution, {tree.data}")


def _parse_distribution_geometric(tree: Tree) -> Geometric:
    p = _parse_frac(tree.children[0])
    return Geometric(p)


def _parse_distribution_uniform(tree: Tree) -> Uniform:
    n = _parse_int(tree.children[0])
    return Uniform(n)


def _parse_distribution_negbinom(tree: Tree) -> NegBinom:
    n = _parse_int(tree.children[0])
    p = _parse_frac(tree.children[1])
    return NegBinom(n, p)


def _parse_distribution_bernoulli(tree: Tree) -> Bernoulli:
    p = _parse_frac(tree.children[0])
    return Bernoulli(p)


def _parse_distribution_dirac(tree: Tree) -> Dirac:
    n = _parse_int(tree.children[0])
    return Dirac(n)


def _parse_guard(tree: Tree, variables: set[str]):
    if tree.data == "lt":
        return _parse_guard_lt(tree, variables)
    if tree.data == "mod":
        return _parse_guard_mod(tree, variables)
    if tree.data == "eq":
        return _parse_guard_eq(tree, variables)
    if tree.data == "leq":
        return _parse_guard_leq(tree, variables)
    if tree.data == "geq":
        return _parse_guard_geq(tree, variables)
    if tree.data == "gt":
        return _parse_guard_gt(tree, variables)
    if tree.data == "land":
        return _parse_guard_land(tree, variables)
    if tree.data == "lor":
        return _parse_guard_lor(tree, variables)
    if tree.data == "neq":
        return _parse_guard_neq(tree, variables)
    if tree.data == "impl":
        return _parse_guard_impl(tree, variables)
    if tree.data == "neg":
        return _parse_guard_neg(tree, variables)
    raise ValueError(f"Unknown guard, {tree.data}")


def _parse_guard_lt(tree: Tree, variables: set[str]) -> LessThan:
    indeterminate = _parse_var(tree.children[0], variables)
    n = _parse_int(tree.children[1])
    return LessThan(indeterminate, n)


def _parse_guard_mod(tree: Tree, variables: set[str]) -> ModuloEquals:
    indeterminate = _parse_var(tree.children[0], variables)
    modulus = _parse_int(tree.children[1])
    residue = _parse_int(tree.children[2])
    return ModuloEquals(indeterminate, modulus, residue)


def _parse_guard_eq(tree: Tree, variables: set[str]) -> Equals:
    indeterminate = _parse_var(tree.children[0], variables)
    n = _parse_int(tree.children[1])
    return Equals(indeterminate, n)


def _parse_guard_leq(tree: Tree, variables: set[str]) -> LessThan:
    indeterminate = _parse_var(tree.children[0], variables)
    n = _parse_int(tree.children[1])
    return LessThan(indeterminate, n + 1)


def _parse_guard_geq(tree: Tree, variables: set[str]) -> Not:
    indeterminate = _parse_var(tree.children[0], variables)
    n = _parse_int(tree.children[1])
    return Not(LessThan(indeterminate, n))


def _parse_guard_gt(tree: Tree, variables: set[str]) -> Not:
    indeterminate = _parse_var(tree.children[0], variables)
    n = _parse_int(tree.children[1])
    return Not(LessThan(indeterminate, n + 1))


def _parse_guard_land(tree: Tree, variables: set[str]) -> And:
    guard1 = _parse_guard(tree.children[0], variables)
    guard2 = _parse_guard(tree.children[1], variables)
    return And(guard1, guard2)


def _parse_guard_neq(tree: Tree, variables: set[str]) -> Not:
    indeterminate = _parse_var(tree.children[0], variables)
    n = _parse_int(tree.children[1])
    return Not(Equals(indeterminate, n))


def _parse_guard_lor(tree: Tree, variables: set[str]) -> Or:
    guard_1 = _parse_guard(tree.children[0], variables)
    guard_2 = _parse_guard(tree.children[1], variables)
    return Or(guard_1, guard_2)


def _parse_guard_impl(tree: Tree, variables: set[str]) -> Implies:
    guard_1 = _parse_guard(tree.children[0], variables)
    guard_2 = _parse_guard(tree.children[1], variables)
    return Implies(guard_1, guard_2)


def _parse_guard_neg(tree: Tree, variables: set[str]) -> Not:
    guard = _parse_guard(tree.children[0], variables)
    return Not(guard)


def _statement_list_to_sequential_comp(statements: list[Statement]) -> Statement:
    if not statements:
        return SkipStatement()
    if len(statements) == 1:
        return statements[0]
    return reduce(
        lambda right, left: SequentialCompositionStatement(left=left, right=right),
        reversed(statements[:-1]),
        statements[-1],
    )


# == Query ==


def _parse_query(tree: Tree, variables: set[str]) -> Query:
    if tree.data == "posterior_prob":
        return _parse_query_posterior_prob(tree.children[0], variables)
    if tree.data == "moment":
        return _parse_query_moment(tree, variables)
    if tree.data == "mixed_moment":
        return _parse_query_mixed_moment(tree, variables)
    raise ValueError(f"Unknown query, {tree.data}")


def _parse_query_posterior_prob(tree: Tree, variables: set[str]):
    guard = _parse_guard(tree, variables)
    return PosteriorProbability(guard)


def _parse_query_moment(tree: Tree, variables: set[str]):
    indeterminate = _parse_var(tree.children[0], variables)
    moment = _parse_int(tree.children[1])
    return UnivariateMoment(indeterminate, moment)


def _parse_query_mixed_moment(tree: Tree, variables: set[str]):
    indeterminate1 = _parse_var(tree.children[0], variables)
    indeterminate2 = _parse_var(tree.children[1], variables)
    return MixedMoment(indeterminate1, indeterminate2)

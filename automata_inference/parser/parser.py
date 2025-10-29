from functools import reduce

from symengine import Rational
from lark import Lark, Tree

from automata_inference.program_statements import (
    SkipStatement,
    AssignStatement,
    IncrementStatement,
    MonusStatement,
    CoinflipStatement,
    IfStatement,
    ObserveStatement,
    Program,
    Statement,
    SequentialCompositionStatement,
)
from automata_inference.guards import LtGuard, ModGuard, EqGuard, LandGuard, NegGuard, Guard
from automata_inference.distributions import (
    Distribution,
    DiracDistribution,
    BernoulliDistribution,
    GeometricDistribution,
    NegBinomialDistribution,
    UniformDistribution,
)

# Heavily inspired by Philipp Schröers' work:
# https://github.com/Philipp15b/probably

GRAMMAR = r"""
%ignore /#.*$/m
%ignore /\/\/.*$/m
%ignore WS
%ignore ";"

%import common.CNAME
%import common.INT
%import common.WS

program: declarations statements

declarations:    declaration*   -> declarations
statements:      statement*     -> statements

declaration:    "var" var       -> var

statement:      "skip"                              -> skip
        |       var ":=" rhs                        -> assignment
        |       var "+=" rhs                        -> increment
        |       var "--"                            -> monus
        |       block "[" frac "]" block            -> probchoice
        |       "if" par_block block "else"? block  -> if
        |       "observe" par_block                 -> observe
        |       "while" par_block block             -> while

block: "{" statement* "}"
par_block: "(" guard ")"

guard:  var "<" INT             -> lt
    |   var "%" INT "="? INT    -> mod
    |   var "=" INT             -> eq
    |   var "<=" INT            -> leq
    |   var ">=" INT            -> geq
    |   var ">" INT             -> gt
    |   guard "&&" guard        -> land
    |   guard "||" guard        -> lor
    |   "!" par_block           -> neg

rhs:    INT                                     -> const
    |   "iid" "(" distribution "," var  ")"     -> iid
    |   distribution                            -> distribution
    |   var                                     -> var

distribution:   "unif" "(" INT ")"                  -> uniform
        |       "geom" "(" frac")"                  -> geometric
        |       "negbinom" "(" INT "," frac ")"     -> negbinom
        |       "bernoulli" "(" frac ")"            -> bernoulli
        |       "dirac" "(" INT ")"                 -> dirac

frac:   INT "/" INT     -> frac

var: CNAME
    """


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
    parser = Lark(GRAMMAR, start="program")
    ast = parser.parse(program)
    return _parse_tree(ast)


def _parse_tree(tree: Tree) -> Program:
    declarations = _parse_declarations(tree.children[0])
    variables = set(declarations)
    statements = _parse_statements(tree.children[1], variables)
    return Program(
        _statement_list_to_sequential_comp(statements),
        any(isinstance(st, ObserveStatement) for st in statements),
        variables,
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
    rhs = _parse_rhs(tree.children[1], indeterminate, variables)
    return AssignStatement(indeterminate, rhs)


def _parse_statement_increment(tree: Tree, variables: set[str]):
    indeterminate = _parse_var(tree.children[0], variables)
    rhs = _parse_rhs(tree.children[1], indeterminate, variables)
    return IncrementStatement(indeterminate, rhs)


def _parse_statement_monus(tree: Tree, variables: set[str]):
    indeterminate = _parse_var(tree.children[0], variables)
    return MonusStatement(indeterminate)


def _parse_statement_probchoice(tree: Tree, variables: set[str]) -> CoinflipStatement:
    lhs = _statement_list_to_sequential_comp(_parse_statements(tree.children[0], variables))
    p = _parse_frac(tree.children[1])
    rhs = _statement_list_to_sequential_comp(_parse_statements(tree.children[2], variables))
    return CoinflipStatement(lhs, p, rhs)


def _parse_statement_if(tree: Tree, variables):
    guard = _parse_guard(tree.children[0].children[0], variables)
    then_statement = _statement_list_to_sequential_comp(_parse_statements(tree.children[1], variables))
    else_statement = _statement_list_to_sequential_comp(_parse_statements(tree.children[2], variables))
    return IfStatement(guard, then_statement, else_statement)


def _parse_statement_observe(tree: Tree, variables: set[str]):
    guard = _parse_guard(tree.children[0].children[0], variables)
    return ObserveStatement(guard)


def _parse_statement_while(tree: Tree, variables: set[str]):
    raise NotImplementedError("While currently not supported :(")


def _parse_frac(tree: Tree) -> Rational:
    if int(str(tree.children[1])) == 0:
        raise ValueError("Division by 0")
    return Rational(tree.children[0], tree.children[1])


def _parse_rhs(tree: Tree, indeterminate: str, variables: set[str]):
    if tree.data == "const":
        return _parse_const(tree)
    if tree.data == "iid":
        return _parse_iid(tree, indeterminate, variables)
    if tree.data == "distribution":
        return _parse_distribution(tree.children[0], indeterminate)
    if tree.data == "var":
        return _parse_var(tree, variables)
    raise ValueError(f"Unknown rhs, {tree.data}")


def _parse_var(tree: Tree, variables: set[str], check_variables: bool =True) -> str:
    indeterminate = str(tree.children[0])
    if indeterminate not in variables and check_variables:
        raise ValueError(f"Variable {indeterminate} not defined.")
    return indeterminate


def _parse_const(tree: Tree) -> int:
    return _parse_int(tree.children[0])


def _parse_int(tree: Tree) -> int:
    return int(str(tree))


def _parse_iid(tree: Tree, indeterminate: str, variables: set[str]) -> tuple[Distribution, str]:
    distribution = _parse_distribution(tree.children[0], indeterminate)
    indeterminate_rhs = _parse_var(tree.children[1], variables)
    return (distribution, indeterminate_rhs)


def _parse_distribution(tree: Tree, indeterminate: str) -> Distribution:
    if tree.data == "geometric":
        return _parse_distribution_geometric(tree, indeterminate)
    if tree.data == "uniform":
        return _parse_distribution_uniform(tree, indeterminate)
    if tree.data == "negbinom":
        return _parse_distribution_negbinom(tree, indeterminate)
    if tree.data == "bernoulli":
        return _parse_distribution_bernoulli(tree, indeterminate)
    if tree.data == "dirac":
        return _parse_distribution_dirac(tree, indeterminate)
    raise ValueError(f"Unknown distribution, {tree.data}")


def _parse_distribution_geometric(tree: Tree, indeterminate: str) -> GeometricDistribution:
    p = _parse_frac(tree.children[0])
    return GeometricDistribution(indeterminate, p)


def _parse_distribution_uniform(tree: Tree, indeterminate: str) -> UniformDistribution:
    n = _parse_int(tree.children[0])
    return UniformDistribution(indeterminate, n)


def _parse_distribution_negbinom(tree: Tree, indeterminate: str) -> NegBinomialDistribution:
    n = _parse_int(tree.children[0])
    p = _parse_frac(tree.children[1])
    return NegBinomialDistribution(indeterminate, n, p)


def _parse_distribution_bernoulli(tree: Tree, indeterminate: str) -> BernoulliDistribution:
    p = _parse_frac(tree.children[0])
    return BernoulliDistribution(indeterminate, p)


def _parse_distribution_dirac(tree: Tree, indeterminate: str) -> DiracDistribution:
    n = _parse_int(tree.children[0])
    return DiracDistribution(indeterminate, n)


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
    if tree.data == "neg":
        return _parse_guard_neg(tree, variables)
    raise ValueError(f"Unknown guard, {tree.data}")


def _parse_guard_lt(tree: Tree, variables: set[str]) -> LtGuard:
    indeterminate = _parse_var(tree.children[0], variables)
    n = _parse_int(tree.children[1])
    return LtGuard(indeterminate, n)


def _parse_guard_mod(tree: Tree, variables: set[str]) -> ModGuard:
    indeterminate = _parse_var(tree.children[0], variables)
    modulus = _parse_int(tree.children[1])
    residue = _parse_int(tree.children[2])
    return ModGuard(indeterminate, modulus, residue)


def _parse_guard_eq(tree: Tree, variables: set[str]) -> EqGuard:
    indeterminate = _parse_var(tree.children[0], variables)
    n = _parse_int(tree.children[1])
    return EqGuard(indeterminate, n)


def _parse_guard_leq(tree: Tree, variables: set[str]) -> Guard:
    indeterminate = _parse_var(tree.children[0], variables)
    n = _parse_int(tree.children[1])
    return LtGuard(indeterminate, n+1)


def _parse_guard_geq(tree: Tree, variables: set[str]) -> Guard:
    indeterminate = _parse_var(tree.children[0], variables)
    n = _parse_int(tree.children[1])
    return NegGuard(LtGuard(indeterminate, n))


def _parse_guard_gt(tree: Tree, variables: set[str]) -> Guard:
    indeterminate = _parse_var(tree.children[0], variables)
    n = _parse_int(tree.children[1])
    return NegGuard(LtGuard(indeterminate, n + 1))


def _parse_guard_land(tree: Tree, variables: set[str]) -> LandGuard:
    guard1 = _parse_guard(tree.children[0], variables)
    guard2 = _parse_guard(tree.children[1], variables)
    return LandGuard(guard1, guard2)


def _parse_guard_lor(tree: Tree, variables: set[str]):
    raise NotImplementedError("kb")


def _parse_guard_neg(tree: Tree, variables: set[str]) -> NegGuard:
    guard = _parse_guard(tree.children[0], variables)
    return NegGuard(guard)


def _statement_list_to_sequential_comp(statements: list[Statement]) -> Statement:
    if len(statements) == 1:
        return statements[0]
    return reduce(
        lambda rhs, lhs: SequentialCompositionStatement(lhs=lhs, rhs=rhs),
        reversed(statements[:-1]),
        statements[-1],
    )

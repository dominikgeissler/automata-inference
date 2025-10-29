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
from automata_inference.guards import LtGuard, ModGuard, EqGuard, GtGuard, LandGuard, NegGuard, Guard
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
    program = open(program_path, "r", encoding="utf-8").read()
    return parse_string(program)


def parse_string(program: str) -> Program:
    parser = get_parser()
    ast = parser.parse(program)
    return _parse_tree(ast)


def get_parser() -> Lark:
    return Lark(GRAMMAR, start="program")


def _parse_tree(tree: Tree) -> Program:
    declarations = _parse_declarations(tree.children[0])
    statements = _parse_statements(tree.children[1])
    return Program(
        _statement_list_to_sequential_comp(statements),
        any(isinstance(st, ObserveStatement) for st in statements),
        set(declarations),
    )


# === Declarations ===
def _parse_declarations(tree: Tree) -> list[str]:
    return [_parse_declaration(decl) for decl in tree.children]


def _parse_declaration(tree: Tree) -> str:
    return _parse_var(tree.children[0])


# === Statements ===
def _parse_statements(tree: Tree):
    return [_parse_statement(t) for t in tree.children]


def _parse_statement(tree: Tree):
    if tree.data == "skip":
        return _parse_statement_skip(tree)
    if tree.data == "assignment":
        return _parse_statement_assignment(tree)
    if tree.data == "increment":
        return _parse_statement_increment(tree)
    if tree.data == "monus":
        return _parse_statement_monus(tree)
    if tree.data == "probchoice":
        return _parse_statement_probchoice(tree)
    if tree.data == "if":
        return _parse_statement_if(tree)
    if tree.data == "observe":
        return _parse_statement_observe(tree)
    if tree.data == "while":
        return _parse_statement_while(tree)
    raise Exception("Not recognized")


def _parse_statement_skip(tree: Tree):
    return SkipStatement()


def _parse_statement_assignment(tree: Tree):
    indeterminate = _parse_var(tree.children[0])
    rhs = _parse_rhs(tree.children[1], indeterminate)
    return AssignStatement(indeterminate, rhs)


def _parse_statement_increment(tree: Tree):
    indeterminate = _parse_var(tree.children[0])
    rhs = _parse_rhs(tree.children[1], indeterminate)
    return IncrementStatement(indeterminate, rhs)


def _parse_statement_monus(tree: Tree):
    indeterminate = _parse_var(tree.children[0])
    return MonusStatement(indeterminate)


def _parse_statement_probchoice(tree: Tree) -> CoinflipStatement:
    lhs = _statement_list_to_sequential_comp(_parse_statements(tree.children[0]))
    p = _parse_frac(tree.children[1])
    rhs = _statement_list_to_sequential_comp(_parse_statements(tree.children[2]))
    return CoinflipStatement(lhs, p, rhs)


def _parse_statement_if(tree: Tree):
    guard = _parse_guard(tree.children[0].children[0])
    then_statement = _statement_list_to_sequential_comp(_parse_statements(tree.children[1]))
    else_statement = _statement_list_to_sequential_comp(_parse_statements(tree.children[2]))
    return IfStatement(guard, then_statement, else_statement)


def _parse_statement_observe(tree: Tree):
    guard = _parse_guard(tree.children[0].children[0])
    return ObserveStatement(guard)


def _parse_statement_while(tree: Tree):
    raise NotImplementedError("While currently not supported :(")


def _parse_frac(tree: Tree) -> Rational:
    if int(str(tree.children[1])) == 0:
        raise Exception("Division by 0")
    return Rational(tree.children[0], tree.children[1])


def _parse_rhs(tree: Tree, indeterminate: str):
    if tree.data == "const":
        return _parse_const(tree)
    if tree.data == "iid":
        return _parse_iid(tree, indeterminate)
    if tree.data == "distribution":
        return _parse_distribution(tree.children[0], indeterminate)
    if tree.data == "var":
        return _parse_var(tree)
    raise Exception("Unknown rhs")


def _parse_var(tree: Tree) -> str:
    return str(tree.children[0])


def _parse_const(tree: Tree) -> int:
    return _parse_INT(tree.children[0])


def _parse_INT(tree: Tree) -> int:
    return int(str(tree))


def _parse_iid(tree: Tree, indeterminate: str) -> tuple[Distribution, str]:
    distribution = _parse_distribution(tree.children[0], indeterminate)
    indeterminate_rhs = _parse_var(tree.children[1])
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
    raise Exception("Unknown distribution")


def _parse_distribution_geometric(tree: Tree, indeterminate: str) -> GeometricDistribution:
    p = _parse_frac(tree.children[0])
    return GeometricDistribution(indeterminate, p)


def _parse_distribution_uniform(tree: Tree, indeterminate: str) -> UniformDistribution:
    n = _parse_INT(tree.children[0])
    return UniformDistribution(indeterminate, n)


def _parse_distribution_negbinom(tree: Tree, indeterminate: str) -> NegBinomialDistribution:
    n = _parse_INT(tree.children[0])
    p = _parse_frac(tree.children[1])
    return NegBinomialDistribution(indeterminate, n, p)


def _parse_distribution_bernoulli(tree: Tree, indeterminate: str) -> BernoulliDistribution:
    p = _parse_frac(tree.children[0])
    return BernoulliDistribution(indeterminate, p)


def _parse_distribution_dirac(tree: Tree, indeterminate: str) -> DiracDistribution:
    n = _parse_INT(tree.children[0])
    return DiracDistribution(indeterminate, n)


def _parse_guard(tree: Tree):
    if tree.data == "lt":
        return _parse_guard_lt(tree)
    if tree.data == "mod":
        return _parse_guard_mod(tree)
    if tree.data == "eq":
        return _parse_guard_eq(tree)
    if tree.data == "leq":
        return _parse_guard_leq(tree)
    if tree.data == "geq":
        return _parse_guard_geq(tree)
    if tree.data == "gt":
        return _parse_guard_gt(tree)
    if tree.data == "land":
        return _parse_guard_land(tree)
    if tree.data == "lor":
        return _parse_guard_lor(tree)
    if tree.data == "neg":
        return _parse_guard_neg(tree)
    raise Exception("Unknown guard")


def _parse_guard_lt(tree: Tree) -> LtGuard:
    indeterminate = _parse_var(tree.children[0])
    n = _parse_INT(tree.children[1])
    return LtGuard(indeterminate, n)


def _parse_guard_mod(tree: Tree) -> ModGuard:
    indeterminate = _parse_var(tree.children[0])
    modulus = _parse_INT(tree.children[1])
    residue = _parse_INT(tree.children[2])
    return ModGuard(indeterminate, modulus, residue)


def _parse_guard_eq(tree: Tree) -> EqGuard:
    indeterminate = _parse_var(tree.children[0])
    n = _parse_INT(tree.children[1])
    return EqGuard(indeterminate, n)


def _parse_guard_leq(tree: Tree) -> Guard:
    indeterminate = _parse_var(tree.children[0])
    n = _parse_INT(tree.children[1])
    return NegGuard(GtGuard(indeterminate, n))


def _parse_guard_geq(tree: Tree) -> Guard:
    indeterminate = _parse_var(tree.children[0])
    n = _parse_INT(tree.children[1])
    return NegGuard(LtGuard(indeterminate, n))


def _parse_guard_gt(tree: Tree) -> GtGuard:
    indeterminate = _parse_var(tree.children[0])
    n = _parse_INT(tree.children[1])
    return GtGuard(indeterminate, n)


def _parse_guard_land(tree: Tree) -> LandGuard:
    guard1 = _parse_guard(tree.children[0])
    guard2 = _parse_guard(tree.children[1])
    return LandGuard(guard1, guard2)


def _parse_guard_lor(tree: Tree):
    raise NotImplementedError("kb")


def _parse_guard_neg(tree: Tree) -> NegGuard:
    guard = _parse_guard(tree.children[0])
    return NegGuard(guard)


def _statement_list_to_sequential_comp(statements: list[Statement]) -> Statement:
    if len(statements) == 1:
        return statements[0]
    return reduce(
        lambda rhs, lhs: SequentialCompositionStatement(lhs=lhs, rhs=rhs),
        reversed(statements[:-1]),
        statements[-1],
    )

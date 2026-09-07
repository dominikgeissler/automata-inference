from pathlib import Path

from fractions import Fraction

from automata_inference.automata.factory import PGAFactory
from automata_inference.parser.parser import parse
from automata_inference.programs.handlers.query_handler import QueryHandler
from automata_inference.programs.handlers.statement_handler import StatementHandler


def test_ictac_inference():
    program_path = Path(__file__).parents[2] / "examples" / "ICTAC.pgcl"
    program = parse(str(program_path))
    
    result = StatementHandler(program.variables).compile_program(
        program, PGAFactory.one()
    )
    
    assert program.query is not None
    assert QueryHandler.evaluate_query(program.query, result) == Fraction(2, 11)
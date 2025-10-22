import time
from automata_inference.automata_factory import PGAFactory
from automata_inference.visualizer import visualize
from automata_inference.parser.parser import parse


program = parse("examples/ICTAC.pgcl")
input_pga = PGAFactory.one((program.variables | {"1"}))
start = time.time()
out = program.apply_semantics(input_pga)
print(f"Duration: {time.time() - start}")
visualize(out, "bla", view=True)

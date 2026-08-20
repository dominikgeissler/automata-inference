import time
from automata_inference.automata_factory import PGAFactory
from automata_inference.visualizer import visualize
from automata_inference.parser.parser import parse, parse_string
from automata_inference.transform import transform_to_flatten

program = parse("examples/ICTAC.pgcl")
# program = parse_string("""
#                        var X;
#                        var Y;
#                        X := geom(1/2);
#                        Y += 1
#                        """)
input_pga = PGAFactory.one((program.variables | {"1"}))
start = time.time()
out = program.apply_semantics(input_pga)

transform_to_flatten(out, 20, "X")

print(f"Duration: {time.time() - start}")
visualize(out, "result", view=True)
# print(out.get_probability_mass())

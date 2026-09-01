import time
from automata_inference.automata_factory import PGAFactory
from automata_inference.visualizer import visualize
from automata_inference.parser.parser import parse, parse_string

# program = parse("examples/ICTAC.pgcl")
program = parse("examples/piranha.pgcl")
# program = parse_string("""
#                        var X;
#                        var Y;
#                        X := geom(1/2);
#                        X += 1;
#                        Y += geom(1/2)
#                        """)
input_pga = PGAFactory.one((program.variables | {"1"}))
# start = time.time()
out = program.apply_semantics(input_pga)

if program.query:
    print(f"QUERY: {program.evaluate_query(out)}")

# transform_to_flatten(out, 50, "X")
# import symengine
# out = PGAFactory.geometric(indeterminate="Y",p=symengine.Rational(1, 2), indeterminates={"X", "Y", "1"})

# second_moment = transform_to_flatten(out, 2, "X")
# first_moment = transform_to_flatten(out, 1, "X")
# print(f"Variance: {second_moment - first_moment**2}")

# # print(f"Duration: {time.time() - start}")
# visualize(out, "result", view=True)
# print(out.get_probability_mass())

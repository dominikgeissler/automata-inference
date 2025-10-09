from automata_factory import PGAFactory, minimize
from visualizer import visualize
from examples.ictac_example import get_ictac_example

program = get_ictac_example()

print(program)
input_pga = PGAFactory.one()
out = program.apply_semantics(input_pga)

out = minimize(out)
visualize(out, view=True)
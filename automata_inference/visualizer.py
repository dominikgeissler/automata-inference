from automata_factory import Automaton, PGA
from graphviz import Digraph


def visualize(aut: Automaton, out_path="aut", view=False):
    dot = Digraph(comment="Automaton visualization")

    is_pga = isinstance(aut, PGA)
    if not is_pga:
        for state in aut.states:
            dot.node(state, shape="circle")

    if is_pga:
        for weight, state in aut.initial:
            dot.node(f"init_{state}", label="", shape="point")
            dot.edge(f"init_{state}", state, label=str(weight))

        for weight, state in aut.final:
            dot.node(f"final_{state}", label="", shape="point")
            dot.edge(state, f"final_{state}", label=str(weight))

    else:
        for state in aut.initial:
            dot.node(f"init_{state}", label="", shape="point")
            dot.edge(f"init_{state}", state)

        for state in aut.final:
            dot.node(state, shape="doublecircle")

    for indeterminate, transitions in aut.transition_matrix.items():
        for trans in transitions:
            if is_pga:
                weight, s, t = trans
                label = (
                    f"{weight}{indeterminate}" if indeterminate != 1 else str(weight)
                )

            else:
                s, t = trans
                label = indeterminate if indeterminate != 1 else ""

            dot.edge(s, t, label=label)

    dot.render(out_path, format="pdf", view=view, cleanup=True)

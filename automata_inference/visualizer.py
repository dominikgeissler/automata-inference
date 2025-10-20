from graphviz import Digraph

from automata_inference.automata_factory import Automaton, PGA

CONSTANT_KEY = "1"


def visualize(aut: Automaton, out_path="aut", view=True):
    """Visualizes the given automaton.

    Args:
        aut (Automaton): The automaton to be visualized.
        out_path (str, optional): The path the visualization should be saved at. Defaults to "aut".
        view (bool, optional): Whether the file should be opened automatically. Defaults to False.
    """
    dot = Digraph(comment="Automaton visualization")

    is_pga = isinstance(aut, PGA)  # or any(isinstance(el, tuple) for el in aut.initial | aut.final)

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

    self_loops: dict[str, list[str]] = {q: [] for q in aut.states}
    for indeterminate, transitions in aut.transition_matrix.items():
        for trans in transitions:
            if is_pga:
                print(dot)
                weight, s, t = trans
                label = f"{weight}{indeterminate}" if indeterminate != CONSTANT_KEY else str(weight)
            else:
                s, t = trans
                label = indeterminate if indeterminate != CONSTANT_KEY else ""

            if s == t:
                if not label:
                    # No epsilon self-loops
                    continue
                self_loops[s].append(label)
            else:
                dot.edge(s, t, label=label)
    for state, labels in self_loops.items():
        dot.edge(state, state, ",".join(labels))
    dot.render(out_path, format="pdf", view=view, cleanup=True)

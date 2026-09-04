from graphviz import Digraph

from automata_inference.automata.model import PGA, Automaton, StateLike


def visualize(aut: Automaton, out_path="aut", view=False):
    """Visualizes the given automaton.

    Args:
        aut (Automaton): The automaton to be visualized.
        out_path (str, optional): The path the visualization should be saved at. Defaults to "aut".
        view (bool, optional): Whether the file should be opened automatically. Defaults to True.
    """
    dot = Digraph(comment="Automaton visualization")

    def node_id(state):
        return str(state)

    is_pga = isinstance(aut, PGA)
    for state in aut.states:
        dot.node(node_id(state), shape="circle")

    if is_pga:
        for weight, state in aut.initial:
            initial_id = f"init_{node_id(state)}"
            dot.node(initial_id, label="", shape="point")
            dot.edge(initial_id, node_id(state), label=str(weight))

        for weight, state in aut.final:
            final_id = f"final_{node_id(state)}"
            dot.node(final_id, label="", shape="point")
            dot.edge(node_id(state), final_id, label=str(weight))

    else:
        for state in aut.initial:
            initial_id = f"init_{node_id(state)}"
            dot.node(initial_id, label="", shape="point")
            dot.edge(initial_id, node_id(state))

        for state in aut.final:
            dot.node(node_id(state), shape="doublecircle")

    self_loops: dict[StateLike, list[str]] = {node_id(state): [] for state in aut.states}
    for transition in aut.transition_matrix:
        source = node_id(transition.source)
        target = node_id(transition.target)
        symbol = transition.symbol
        weight = transition.weight

        if is_pga:
            weight_label = str(weight) if weight != 1 or symbol is None else ""
            label = f"{weight_label}{symbol}" if symbol is not None else weight_label
        else:
            label = symbol or ""

        if source == target:
            if label:
                self_loops[source].append(label)
        else:
            dot.edge(source, target, label=label)

    for state, labels in self_loops.items():
        if labels:
            dot.edge(str(state), str(state), ",".join(labels))
    dot.render(out_path, format="pdf", view=view, cleanup=True)

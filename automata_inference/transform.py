from automata_inference.automata_factory import PGA, minimize
from symengine import Rational
from math import comb
from automata_inference.visualizer import visualize

def _has_transition(d: dict, x: str | set[str], s: str, t: str) -> Rational:
    if isinstance(x, set):
        for v in x:
            values = d[v]
            for a, s1, t1 in values:
                if s == s1 and t == t1:
                    return a
    else:
        values = d[x]
        for a, s1, t1 in values:
            if s == s1 and t == t1:
                return a
    return 0


def transform_to_flatten(pga: PGA, n: int, x: str):
    pga_states = sorted(pga.states)
    visualize(pga, out_path="blaa", view=False)

    # i represents the index of the state stored in pga_states
    # j represents the layer
    new_states = {f"({i},{j})" for i in range(len(pga_states)) for j in range(n + 1)}

    new_transition_matrix = {"1": []}

    # Different Layer transitions
    new_transition_matrix["1"].extend(
        [
            (
                comb(i, j) * _has_transition(pga.transition_matrix, x, pga_states[s], pga_states[t]),
                f"({s},{i})",
                f"({t},{j})",
            )
            for s in range(len(pga_states))
            for t in range(len(pga_states))
            for i in range(n + 1)
            for j in range(n + 1)
            if _has_transition(pga.transition_matrix, x, pga_states[s], pga_states[t]) and i > j
        ]
    )

    # Same Layer transitions
    new_transition_matrix["1"].extend(
        (
            _has_transition(pga.transition_matrix, set(pga.transition_matrix.keys()), pga_states[s], pga_states[t]),
            f"({s},{i})",
            f"({t},{i})",
        )
        for s in range(len(pga_states))
        for t in range(len(pga_states))
        for i in range(n + 1)
        if _has_transition(pga.transition_matrix, set(pga.transition_matrix.keys()), pga_states[s], pga_states[t])
    )

    new_initial = {(v, f"({pga_states.index(s)},{n})") for (v, s) in pga.initial if v}

    new_final = {(v, f"({pga_states.index(s)},{0})") for (v, s) in pga.final if v}

    aut = PGA(new_states, new_transition_matrix, new_initial, new_final)  # not rly a PGA though

    aut = minimize(aut, aut.transition_matrix.keys())

    visualize(aut, view=True)

    print(aut.get_probability_mass())  # compute the mass -> corresponding moment

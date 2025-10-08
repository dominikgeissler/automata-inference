from automaton import Automaton, PGA
from automata_factory import PGAFactory

CONSTANT_KEY = 1


def minimize(aut: Automaton):
    aut = remove_noncoaccessible_states(aut)
    if isinstance(aut, PGA):
        aut = merge_states(aut)
    return aut


def remove_noncoaccessible_states(aut: Automaton):
    is_pga = isinstance(aut, PGA)

    def get_state(possible_weighted_state):
        return (
            possible_weighted_state[1]
            if isinstance(possible_weighted_state, tuple)
            else possible_weighted_state
        )

    successors = {q: set() for q in aut.states}
    predecessors = {q: set() for q in aut.states}
    print(aut.states)
    for _, transitions in aut.transition_matrix.items():
        for trans in transitions:
            if is_pga:
                _, s, t = trans
            else:
                s, t = trans
            successors[s].add(t)
            predecessors[t].add(s)

    reachable = set()
    stack = list(get_state(el) for el in aut.initial)

    while stack:
        curr = stack.pop()
        if curr not in reachable:
            reachable.add(curr)
            stack.extend(successors[curr])

    coaccessible = set()
    stack = list(get_state(el) for el in aut.final)

    while stack:
        curr = stack.pop()
        if curr not in coaccessible:
            coaccessible.add(curr)
            stack.extend(predecessors[curr])

    keep = reachable & coaccessible
    if not keep:
        return PGAFactory.zero()

    new_transition_matrix = dict()
    aut.states = keep
    for indeterminate, transitions in aut.transition_matrix.items():
        keep_trans = []
        for trans in transitions:
            if is_pga:
                w, s, t = trans
                if s in keep and t in keep:
                    keep_trans.append((w, s, t))
            else:
                s, t = trans
                if s in keep and t in keep:
                    keep_trans.append((s, t))
        new_transition_matrix[indeterminate] = keep_trans
    aut.transition_matrix = new_transition_matrix

    if is_pga:
        aut.initial = {(w, s) for (w, s) in aut.initial if s in keep}
        aut.final = {(w, s) for (w, s) in aut.final if s in keep}
    else:
        aut.initial = aut.initial & keep
        aut.final = aut.final & keep
        
    print(aut)
    return aut


def merge_states(aut: PGA):
    return aut
    if is_minimal(aut):
        return aut
    # todo implement
    pass


def is_minimal(aut: PGA):
    return len(aut.transition_matrix[CONSTANT_KEY]) == 0

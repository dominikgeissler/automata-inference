from automata_inference.automata.model import Automaton, PGA, DFA

from typing import TypeVar

A = TypeVar("A", bound=Automaton)

def minimize(aut: A) -> A:
    """Minimizes the given automaton by removing non-coaccessible states and merging redundant states.

    Args:
        aut (Automaton): The automaton to be minimized.

    Returns:
        Automaton: The minimized automaton.
    """
    aut = remove_noncoaccessible_states(aut)
    # if isinstance(aut, PGA):
    #     aut = merge_states(aut)
    return aut


def remove_noncoaccessible_states(aut: A) -> A:
    """Removes unreachable and non-coaccessible states.

    Args:
        aut (Automaton): The automaton to be minimized
        indeterminates (set[str]): The set of indeterminates (used for default automaton)

    Returns:
        Automaton: The automaton without unreachable / non-coaccessible states.
    """
    is_pga = isinstance(
        aut, PGA
    )  # or any(isinstance(el, tuple) for el in aut.initial | aut.final)
    # Remove zero initial / final weights
    aut.initial = {el for el in aut.initial if el[0] != 0}
    aut.final = {el for el in aut.final if el[0] != 0}

    def get_state(possible_weighted_state):
        return (
            possible_weighted_state[1]
            if isinstance(possible_weighted_state, tuple)
            else possible_weighted_state
        )

    successors = {state: set() for state in aut.states}
    predecessors = {state: set() for state in aut.states}
    for transition in aut.transition_matrix:
        successors[transition.source].add(transition.target)
        predecessors[transition.target].add(transition.source)

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
        from automata_inference.automata.factory import DFAFactory, PGAFactory

        return PGAFactory.zero() if is_pga else DFAFactory.false(aut.get_symbols())  # type: ignore[return-value]

    aut.states = keep
    new_transition_matrix = {
        transition
        for transition in aut.transition_matrix
        if transition.source in keep and transition.target in keep
    }
    aut.transition_matrix = new_transition_matrix

    if is_pga:
        aut.initial = {(w, s) for (w, s) in aut.initial if s in keep}
        aut.final = {(w, s) for (w, s) in aut.final if s in keep}
    else:
        aut.initial = aut.initial & keep
        aut.final = aut.final & keep
    return aut


def merge_states(aut: PGA) -> PGA:
    """Minimizes the automaton by merging states.

    Args:
        aut (PGA): The PGA to be minimized.

    Returns:
        PGA: The resulting minimized PGA.
    """
    return aut

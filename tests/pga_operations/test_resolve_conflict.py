from automata_inference.automata_factory import resolve_conflict, PGA


def test_no_conflict():
    aut1 = PGA(set(["q0"]), dict(), set(), set())
    aut2 = PGA(set(["q1"]), dict(), set(), set())

    new_aut2 = resolve_conflict(aut1, aut2)
    assert aut2 == new_aut2  # Nothing changed


def test_conflict():
    aut1 = PGA(set(["q0", "q1"]), {"X": [(1, "q0", "q1")], "Y": [(1, "q1", "q0")]}, {(1, "q0")}, {(1, "q1")})
    aut2 = aut1
    assert aut1 == aut2
    aut2 = resolve_conflict(aut1, aut2)
    assert aut1 != aut2
    assert aut1.states.isdisjoint(aut2.states)
    for v in ["X", "Y"]:
        assert len(aut1.transition_matrix[v]) == len(aut2.transition_matrix[v])
    assert len(aut1.initial) == len(aut2.initial)
    assert len(aut1.final) == len(aut2.final)

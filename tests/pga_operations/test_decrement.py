# from symengine import Rational

# from automata_inference.automata.model import PGA, State, Transition
# from tests.utils import AutomatonTestUtils

# make_pga = AutomatonTestUtils.create_pga
# assert_pgas_equal = AutomatonTestUtils.assert_equal_pga

# # FIXME
def test():
    assert False

# def test_decrement_no_change():
#     """No transition with the requested indeterminate."""
#     aut = make_pga(0, 1, [(0, 0, "Y", Rational(1, 2))], {(1, 0)}, {(1, 0)})
#     expected = PGA(
#         {State(0, 0), State(1, 0)},
#         [Transition(State(0, 0), State(0, 0), "Y", Rational(1, 2))],
#         {(1, State(0, 0)), (1, State(1, 0))},
#         {(1, State(0, 0))},
#     )
#     assert_pgas_equal(expected, aut.decrement("X"))


# def test_decrement_no_branching():
#     """A singular branch with the requested indeterminate present."""
#     aut = make_pga(0, 1, [(0, 0, "X", Rational(1, 2))], {(1, 0)}, {(1, 0)})
#     p00 = product_state(0, 0, 0)
#     p01 = product_state(0, 0, 1)
#     expected = PGA(
#         {State(0, 0), p00, p01},
#         [Transition(p00, p01, weight=Rational(1, 2))],
#         {(1, State(0, 0)), (1, p00)},
#         {(Rational(1, 2), State(0, 0)), (Rational(1, 2), p01)},
#     )
#     assert_pgas_equal(expected, aut.decrement("X"))


# def test_decrement_branching_no_constant():
#     """Branching automaton where the coefficient of X^0 is zero."""
#     aut = make_pga(
#         0,
#         3,
#         [(0, 1, "X", Rational(1, 2)), (0, 2, "X", Rational(1, 2))],
#         {(1, 0)},
#         {(1, 1), (1, 2)},
#     )
#     p00 = product_state(0, 0, 0)
#     p11 = product_state(0, 1, 1)
#     p21 = product_state(0, 2, 1)
#     expected = PGA(
#         {p00, p11, p21},
#         [Transition(p00, p11, weight=Rational(1, 2)), Transition(p00, p21, weight=Rational(1, 2))],
#         {(1, p00)},
#         {(1, p11), (1, p21)},
#     )
#     assert_pgas_equal(expected, aut.decrement("X"))

#     aut = make_pga(
#         2,
#         4,
#         [
#             (0, 1, "X", Rational(1, 2)),
#             (0, 2, "X", Rational(1, 2)),
#             (1, 3, "X", 1),
#         ],
#         {(1, 0)},
#         {(1, 2), (1, 3)},
#     )
#     p20 = product_state(2, 0, 0)
#     p21 = product_state(2, 1, 1)
#     p22 = product_state(2, 2, 1)
#     p23 = product_state(2, 3, 1)
#     expected = PGA(
#         {p20, p21, p22, p23},
#         [
#             Transition(p20, p21, weight=Rational(1, 2)),
#             Transition(p20, p22, weight=Rational(1, 2)),
#             Transition(p21, p23, "X"),
#         ],
#         {(1, p20)},
#         {(1, p22), (1, p23)},
#     )
#     assert_pgas_equal(expected, aut.decrement("X"))


# def test_decrement_branching_constant():
#     """Branching automaton where the coefficient of X^0 is nonzero."""
#     aut = make_pga(
#         0,
#         3,
#         [(0, 1, "X", Rational(1, 2)), (0, 2, "X", Rational(1, 2))],
#         {(1, 0)},
#         {(1, 0), (1, 1), (1, 2)},
#     )
#     p00 = product_state(0, 0, 0)
#     p11 = product_state(0, 1, 1)
#     p21 = product_state(0, 2, 1)
#     expected = PGA(
#         {State(0, 0), p00, p11, p21},
#         [Transition(p00, p11, weight=Rational(1, 2)), Transition(p00, p21, weight=Rational(1, 2))],
#         {(1, State(0, 0)), (1, p00)},
#         {(1, State(0, 0)), (1, p11), (1, p21)},
#     )
#     assert_pgas_equal(expected, aut.decrement("X"))

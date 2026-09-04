from symengine import Rational

from tests.utils import AutomatonTestUtils

create_pga = AutomatonTestUtils.create_pga
assert_equal_pga = AutomatonTestUtils.assert_equal_pga

class TestOneSubs:
    """Tests substitution by 1."""

    def test_no_change(self):
        """Nothing changes."""
        aut = create_pga(
            0, 1, [(0,0,"X", Rational(1,2))],[(1, 0)], [(Rational(1,2), 0)]
        )
        # Nothing should change
        assert_equal_pga(aut, aut.substitute("Y", 1))

    def test_dirac_pga(self):
        """One transition between two states changes."""
        aut = create_pga(0, 2, [(0, 1, "X", 1)], [(1,0)], [(1,1)])
        expected = create_pga(0, 2, [(0, 1, None, 1)], [(1,0)], [(1,1)])
        assert_equal_pga(expected, aut.substitute("X", 1))

    def test_geometric_pga(self):
        """One self-loop changes"""
        aut = create_pga(
            0, 1, [(0,0,"Y", Rational(1,2))],[(1, 0)], [(Rational(1,2), 0)]
        )
        expected = create_pga(
            0, 1, [(0,0, None , Rational(1,2))],[(1, 0)], [(Rational(1,2), 0)]
        )

        assert_equal_pga(expected, aut.substitute("Y", 1))


class TestZeroSubs:
    """Tests substitution by 0."""

    def test_no_change(self):
        """Nothing changes."""
        aut = create_pga(
            0, 1, [(0,0,"X", Rational(1,2))],[(1, 0)], [(Rational(1,2), 0)]
        )
        # Nothing should change
        assert_equal_pga(aut, aut.substitute("Y", 0))

    def test_dirac_pga(self):
        """One transition between two states changes."""
        aut = create_pga(0, 2, [(0, 1, "X", 1)], [(1,0)], [(1,1)])

        actual = aut.substitute("X", 0)
        
        # We expect the "zero"-PGA
        assert len(actual.states) == 1, "Only one state should remain."
        assert len(actual.transition_matrix) == 0, "No transitions should be present."
        assert len(actual.final) == 0, "No final states should be present."

    def test_geometric_pga(self):
        """One self-loop changes"""
        aut = create_pga(
            0, 1, [(0,0,"Y", Rational(1,2))],[(1, 0)], [(Rational(1,2), 0)]
        )
        expected = create_pga(
            0, 1, [],[(1, 0)], [(Rational(1,2), 0)]
        )

        # Transition should disappear
        assert_equal_pga(expected, aut.substitute("Y", 0))

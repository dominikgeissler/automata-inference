from automata_inference.automata_factory import PGAFactory

CONSTANT_KEY = 1

class TestOneSubs:
    def test_zero_pga(self):
        pga = PGAFactory.zero()
        pga_subs = pga.substitute("X", 1)
        assert pga == pga_subs  # Nothing should change

    def test_dirac_pga(self):
        pga = PGAFactory.dirac("X", 1)
        pga_subs = pga.substitute("X", 1)
        assert pga != pga_subs
        assert not pga_subs.transition_matrix["X"]
        q0, q1 = pga_subs.states
        assert pga_subs.transition_matrix[CONSTANT_KEY] == [(1, q0, q1)] or pga_subs.transition_matrix[CONSTANT_KEY] == [(1, q1, q0)] 
        assert len(pga_subs.transition_matrix[CONSTANT_KEY]) == 1
        assert pga.states == pga_subs.states and pga.initial == pga_subs.initial and pga.final == pga_subs.final
    
    def test_geometric_pga(self):
        pga = PGAFactory.geometric("X", 0.5)
        pga_subs = pga.substitute("X", 1)
        
        assert pga != pga_subs
        assert not pga_subs.transition_matrix["X"]
        assert len(pga_subs.transition_matrix[CONSTANT_KEY]) == 1
        q0 = pga_subs.states.pop()
        assert pga_subs.transition_matrix[CONSTANT_KEY] == [(0.5, q0, q0)]
        assert pga.states == pga_subs.states and pga.initial == pga_subs.initial and pga.final == pga_subs.final
    

class TestZeroSubs:
    def test_zero_pga(self):
        pga = PGAFactory.zero()
        pga_subs = pga.substitute("X", 0)
        assert pga == pga_subs  # Nothing should change  

    def test_dirac_pga(self):
        pga = PGAFactory.dirac("X", 1)
        pga_subs = pga.substitute("X", 0)
        
        assert pga != pga_subs
        assert not pga_subs.transition_matrix["X"]
        assert len(pga_subs.transition_matrix[CONSTANT_KEY]) == 0
        assert pga.states == pga_subs.states and pga.initial == pga_subs.initial and pga.final == pga_subs.final
    
    def test_geometric_pga(self):
        pga = PGAFactory.geometric("X", 0.5)
        pga_subs = pga.substitute("X", 0)
        
        assert pga != pga_subs
        assert not pga_subs.transition_matrix["X"]
        assert len(pga_subs.transition_matrix[CONSTANT_KEY]) == 0
        assert pga.states == pga_subs.states and pga.initial == pga_subs.initial and pga.final == pga_subs.final
    

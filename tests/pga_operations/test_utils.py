from automata_inference.automata_factory import is_probability, reflexive_closure

def test_is_probability():
    f = 0.5
    assert is_probability(f)
    f = -1
    assert not is_probability(f)
    f = 100
    assert not is_probability(f)
    

def test_reflexive_closure():
    pass
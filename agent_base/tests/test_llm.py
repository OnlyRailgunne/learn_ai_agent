from llm import FakeLLM

def test_fake_llm_decide():
    llm = FakeLLM()
    
    assert llm.decide("1+2")["tool"] == "calculator"
    assert llm.decide("3-1")["tool"] == "calculator"
    assert llm.decide("4*5")["tool"] == "calculator"
    assert llm.decide("10/2")["tool"] == "calculator"

def test_fake_llm_generate_response():
    llm = FakeLLM()
    
    assert llm.generate_response("Hello") == "计算结果是: Hello"
import pytest
from app.translator import translate, TranslationError

def test_st():
    r=translate("MotorRun := Start AND NOT Stop;","st","codesys")
    assert r["output"]=="MotorRun := (Start AND NOT (Stop));"

def test_ld():
    r=translate("Run := A AND NOT B;","ld","generic")
    assert "[ A ]" in r["output"] and "[/ B ]" in r["output"]

@pytest.mark.parametrize("source",["Run := TON(A);","Run := A + B;","Run := A; Extra := B;","Run := A (* comment *);"])
def test_reject(source):
    with pytest.raises(TranslationError):
        translate(source,"st","generic")

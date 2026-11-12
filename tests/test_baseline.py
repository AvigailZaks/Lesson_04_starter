import pytest
import baseline.tasks

@pytest.mark.req("BASELINE-04")
def test_first_missing_returns_first_missing_item():
    res = baseline.tasks.first_missing(["item1","item2","item3","item4"],["item1","item2","item4"])
    assert res == "item3"
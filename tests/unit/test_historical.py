import pytest
from src.api.historical import HistoricalData

def test_unknown_uic_raises():
    h = HistoricalData()
    with pytest.raises(ValueError, match="No Yahoo ticker"):
        h.get_bars(99999)

def test_eurusd_mapped():
    h = HistoricalData()
    assert h.UIC_TO_YAHOO[21] == "EURUSD=X"

def test_apple_mapped():
    h = HistoricalData()
    assert h.UIC_TO_YAHOO[211] == "AAPL"

def test_spy_mapped():
    h = HistoricalData()
    assert h.UIC_TO_YAHOO[36590] == "SPY"
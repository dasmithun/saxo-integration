from src.api.historical import HistoricalData

h = HistoricalData()

print("=== EURUSD (1h bars) ===")
h.get_bars(21, period="5d", interval="1h")

print()
print("=== Apple (1d bars) ===")
h.get_bars(211, period="1mo", interval="1d")
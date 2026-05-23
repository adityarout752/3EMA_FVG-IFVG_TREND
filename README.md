# NAS100 IFVG Backtester

Deterministic backtest engine for NAS100 IFVG continuation strategy using pandas + vectorbt.

## Quick Start

```bash
pip install -r requirements.txt
python -m src.app.run_backtest --csv data/raw/your_5m_data.csv
```

Or fetch from yfinance:

```bash
python -m src.app.run_backtest --start 2026-01-01T00:00:00 --end 2026-03-01T00:00:00
```

FTMO/MT5 (default provider in config):

```bash
# set env vars first: FTMO_LOGIN, FTMO_PASSWORD, FTMO_SERVER, MT5_TERMINAL_PATH (optional)
python -m src.app.run_backtest --start 2026-01-01T00:00:00 --end 2026-03-01T00:00:00
```

## Outputs

- `output/trades/trade_log.csv`
- `output/reports/summary.json`
- `output/reports/report.html`
- `output/reports/monte_carlo.csv` (if trades exist)
- `output/charts/entries.png`
- `output/charts/equity_curve.png` (if vectorbt installed)

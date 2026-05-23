"""CLI entrypoint for running the NAS100 IFVG backtest pipeline."""

import argparse
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from src.analytics.monte_carlo import bootstrap_total_return_distribution
from src.data.loader import (
    load_5m_data_from_csv,
    load_5m_data_from_mt5,
    load_5m_data_from_yfinance,
    resolve_mt5_credentials,
    save_dataframe,
)
from src.data.timezone_utils import ensure_timezone
from src.features.bias_engine import add_bias_columns
from src.features.ema import attach_htf_ema_columns
from src.features.fvg import add_fvg_columns
from src.features.ifvg import add_ifvg_confirmation_columns
from src.features.session_filter import add_session_flag
from src.reporting.exporter import export_dataframe, export_json
from src.reporting.plots import plot_equity_curve, plot_price_with_entries
from src.reporting.summary_report import build_summary_payload
from src.reporting.trade_log import build_trade_log
from src.execution.vectorbt_runner import run_vectorbt_portfolio
from src.strategy.state_machine import IFVGStateMachine


def load_config(path: str) -> dict[str, Any]:
    """Load YAML configuration from disk."""
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def build_feature_dataframe(df_5m: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    """Apply full feature pipeline for bias/session/FVG/IFVG detection.

    Args:
        df_5m: Validated 5-minute OHLCV dataframe.
        config: Runtime configuration dictionary.

    Returns:
        Feature-complete dataframe used by state machine execution.
    """
    feature_df = attach_htf_ema_columns(df_5m, ema_length=int(config["ema_length"]))
    feature_df = add_bias_columns(feature_df)
    feature_df = add_session_flag(
        feature_df,
        start_time=config["session"]["start"],
        end_time=config["session"]["end"],
    )
    feature_df = add_fvg_columns(feature_df)
    feature_df = add_ifvg_confirmation_columns(feature_df)
    return feature_df


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for data source and runtime options."""
    parser = argparse.ArgumentParser(description="Run NAS100 IFVG strategy backtest.")
    parser.add_argument("--config", default="config/strategy.yaml", help="Path to strategy config yaml.")
    parser.add_argument("--csv", default="", help="Path to local OHLCV CSV file.")
    parser.add_argument("--start", default="", help="Start datetime ISO format for market data pull.")
    parser.add_argument("--end", default="", help="End datetime ISO format for market data pull.")
    return parser.parse_args()


def main() -> None:
    """Execute full backtest workflow and export results."""
    args = parse_args()
    config = load_config(args.config)
    timezone_name = config["session"]["timezone"]

    data_cfg = config.get("data", {})
    provider = str(data_cfg.get("provider", "ftmo_mt5")).lower()

    if args.csv:
        candles = load_5m_data_from_csv(args.csv, timezone_name=timezone_name)
    else:
        if not args.start or not args.end:
            raise ValueError("When --csv is not provided, both --start and --end are required.")
        start_dt = datetime.fromisoformat(args.start)
        end_dt = datetime.fromisoformat(args.end)

        if provider in {"ftmo", "mt5", "ftmo_mt5"}:
            creds = resolve_mt5_credentials(data_cfg)
            candles = load_5m_data_from_mt5(
                symbol=data_cfg["symbol"],
                start=start_dt,
                end=end_dt,
                target_timezone=timezone_name,
                login=creds["login"],
                password=creds["password"],
                server=creds["server"],
                terminal_path=creds["terminal_path"],
            )
        elif provider == "yfinance":
            candles = load_5m_data_from_yfinance(
                symbol=data_cfg["symbol"],
                start=start_dt,
                end=end_dt,
                target_timezone=timezone_name,
            )
        else:
            raise ValueError(f"Unsupported data provider in config: {provider}")

    candles = ensure_timezone(candles, timezone_name=timezone_name)
    feature_df = build_feature_dataframe(candles, config)
    save_dataframe(feature_df, "data/processed/feature_df.csv")

    machine = IFVGStateMachine(reward_ratio=float(config["risk"]["reward_ratio"]))
    result = machine.run(feature_df)
    trade_log = build_trade_log(result.trades)
    export_dataframe(trade_log, "output/trades/trade_log.csv")

    portfolio = run_vectorbt_portfolio(feature_df["Close"], result, freq="5min")
    equity_curve = portfolio.value() if portfolio is not None else pd.Series(dtype=float)

    summary = build_summary_payload(trade_log, equity_curve=equity_curve if not equity_curve.empty else None)
    monte_carlo_df = bootstrap_total_return_distribution(trade_log, n_scenarios=1000)
    summary["monte_carlo"] = monte_carlo_df.describe().to_dict() if not monte_carlo_df.empty else {}

    export_json(summary, "output/reports/summary.json")
    if not monte_carlo_df.empty:
        export_dataframe(monte_carlo_df, "output/reports/monte_carlo.csv")

    plot_price_with_entries(
        df=feature_df,
        entries_long=result.entries_long,
        entries_short=result.entries_short,
        output_path="output/charts/entries.png",
    )
    if not equity_curve.empty:
        plot_equity_curve(equity_curve, output_path="output/charts/equity_curve.png")

    Path("output/reports").mkdir(parents=True, exist_ok=True)
    print("Backtest completed.")
    print(f"Processed candles: {len(feature_df)}")
    print(f"Closed trades: {len(trade_log)}")
    print("Reports saved under output/.")


if __name__ == "__main__":
    main()

"""Deterministic IFVG state machine for sequential setup detection and trading."""

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

from src.core.enums import Direction, StrategyState
from src.core.types import TradeRecord
from src.strategy.risk_model import compute_stop_take_profit
from src.strategy.setup_detector import is_counter_trend_fvg_row, is_counter_trend_pullback
from src.strategy.trade_manager import evaluate_exit_on_bar, force_exit_trade


@dataclass
class StrategyRunResult:
    """Container for generated signal arrays and completed trades."""

    entries_long: pd.Series
    entries_short: pd.Series
    exits_long: pd.Series
    exits_short: pd.Series
    stop_loss: pd.Series
    take_profit: pd.Series
    trades: list[TradeRecord]


class IFVGStateMachine:
    """Run IFVG event-sequence logic with one-trade-at-a-time constraints."""

    def __init__(self, reward_ratio: float = 2.0) -> None:
        """Initialize state machine runtime settings.

        Args:
            reward_ratio: Fixed reward multiple used for TP computation.
        """
        self.reward_ratio = reward_ratio

    def run(self, df: pd.DataFrame) -> StrategyRunResult:
        """Process candles sequentially and produce deterministic trade signals.

        Args:
            df: Feature dataframe with bias/session/FVG columns.

        Returns:
            StrategyRunResult with entries, exits, per-entry SL/TP, and trade log.
        """
        entries_long = pd.Series(False, index=df.index, dtype=bool)
        entries_short = pd.Series(False, index=df.index, dtype=bool)
        exits_long = pd.Series(False, index=df.index, dtype=bool)
        exits_short = pd.Series(False, index=df.index, dtype=bool)
        stop_loss = pd.Series(np.nan, index=df.index, dtype=float)
        take_profit = pd.Series(np.nan, index=df.index, dtype=float)

        state = StrategyState.WAIT_BIAS
        setup_direction: Optional[Direction] = None
        setup_zone_top: Optional[float] = None
        setup_zone_bottom: Optional[float] = None
        open_trade: Optional[TradeRecord] = None
        entry_row_position: Optional[int] = None
        trades: list[TradeRecord] = []

        for pos, (timestamp, row) in enumerate(df.iterrows()):
            session_active = bool(row.get("is_session_active", False))
            long_bias = bool(row.get("long_bias", False))
            short_bias = bool(row.get("short_bias", False))
            close_price = float(row["Close"])

            if open_trade is not None:
                state = StrategyState.MANAGE_TRADE
                if not session_active:
                    force_exit_trade(open_trade, close_price=close_price, reason="SESSION_END")
                    open_trade.exit_time = timestamp
                    if open_trade.direction == Direction.LONG:
                        exits_long.loc[timestamp] = True
                    else:
                        exits_short.loc[timestamp] = True
                    trades.append(open_trade)
                    open_trade = None
                    state = StrategyState.WAIT_BIAS
                    continue

                if entry_row_position is not None and pos > entry_row_position:
                    did_exit, exit_price, reason = evaluate_exit_on_bar(open_trade, row)
                    if did_exit:
                        open_trade.exit_time = timestamp
                        open_trade.exit_price = exit_price
                        open_trade.exit_reason = reason
                        if open_trade.direction == Direction.LONG:
                            exits_long.loc[timestamp] = True
                        else:
                            exits_short.loc[timestamp] = True
                        trades.append(open_trade)
                        open_trade = None
                        state = StrategyState.WAIT_BIAS
                continue

            if not session_active:
                state = StrategyState.WAIT_BIAS
                setup_direction = None
                setup_zone_top = None
                setup_zone_bottom = None
                continue

            if state == StrategyState.WAIT_BIAS:
                if long_bias:
                    setup_direction = Direction.LONG
                    state = StrategyState.WAIT_PULLBACK
                elif short_bias:
                    setup_direction = Direction.SHORT
                    state = StrategyState.WAIT_PULLBACK
                continue

            if state == StrategyState.WAIT_PULLBACK:
                if setup_direction == Direction.LONG and not long_bias:
                    state = StrategyState.WAIT_BIAS
                    setup_direction = None
                    continue
                if setup_direction == Direction.SHORT and not short_bias:
                    state = StrategyState.WAIT_BIAS
                    setup_direction = None
                    continue

                if setup_direction is not None and is_counter_trend_pullback(df, pos, setup_direction):
                    state = (
                        StrategyState.WAIT_BEARISH_FVG
                        if setup_direction == Direction.LONG
                        else StrategyState.WAIT_BULLISH_FVG
                    )
                continue

            if state == StrategyState.WAIT_BEARISH_FVG:
                if not long_bias:
                    state = StrategyState.WAIT_BIAS
                    setup_direction = None
                    continue
                if is_counter_trend_fvg_row(row, Direction.LONG):
                    setup_zone_top = float(row["bearish_fvg_top"])
                    setup_zone_bottom = float(row["bearish_fvg_bottom"])
                    state = StrategyState.WAIT_IFVG_CONFIRMATION
                continue

            if state == StrategyState.WAIT_BULLISH_FVG:
                if not short_bias:
                    state = StrategyState.WAIT_BIAS
                    setup_direction = None
                    continue
                if is_counter_trend_fvg_row(row, Direction.SHORT):
                    setup_zone_top = float(row["bullish_fvg_top"])
                    setup_zone_bottom = float(row["bullish_fvg_bottom"])
                    state = StrategyState.WAIT_IFVG_CONFIRMATION
                continue

            if state == StrategyState.WAIT_IFVG_CONFIRMATION:
                if setup_direction == Direction.LONG and not long_bias:
                    state = StrategyState.WAIT_BIAS
                    setup_direction = None
                    setup_zone_top = None
                    setup_zone_bottom = None
                    continue
                if setup_direction == Direction.SHORT and not short_bias:
                    state = StrategyState.WAIT_BIAS
                    setup_direction = None
                    setup_zone_top = None
                    setup_zone_bottom = None
                    continue

                if (
                    setup_direction == Direction.LONG
                    and setup_zone_top is not None
                    and setup_zone_bottom is not None
                    and close_price > setup_zone_top
                    and setup_zone_bottom < close_price
                ):
                    sl, tp = compute_stop_take_profit(
                        direction=Direction.LONG,
                        entry_price=close_price,
                        stop_price=setup_zone_bottom,
                        reward_ratio=self.reward_ratio,
                    )
                    entries_long.loc[timestamp] = True
                    stop_loss.loc[timestamp] = sl
                    take_profit.loc[timestamp] = tp
                    open_trade = TradeRecord(
                        direction=Direction.LONG,
                        entry_time=timestamp,
                        entry_price=close_price,
                        stop_loss=sl,
                        take_profit=tp,
                    )
                    entry_row_position = pos
                    state = StrategyState.MANAGE_TRADE
                    setup_direction = None
                    setup_zone_top = None
                    setup_zone_bottom = None
                    continue

                if (
                    setup_direction == Direction.SHORT
                    and setup_zone_top is not None
                    and setup_zone_bottom is not None
                    and close_price < setup_zone_bottom
                    and setup_zone_top > close_price
                ):
                    sl, tp = compute_stop_take_profit(
                        direction=Direction.SHORT,
                        entry_price=close_price,
                        stop_price=setup_zone_top,
                        reward_ratio=self.reward_ratio,
                    )
                    entries_short.loc[timestamp] = True
                    stop_loss.loc[timestamp] = sl
                    take_profit.loc[timestamp] = tp
                    open_trade = TradeRecord(
                        direction=Direction.SHORT,
                        entry_time=timestamp,
                        entry_price=close_price,
                        stop_loss=sl,
                        take_profit=tp,
                    )
                    entry_row_position = pos
                    state = StrategyState.MANAGE_TRADE
                    setup_direction = None
                    setup_zone_top = None
                    setup_zone_bottom = None

        if open_trade is not None:
            last_ts = df.index[-1]
            last_close = float(df.iloc[-1]["Close"])
            force_exit_trade(open_trade, close_price=last_close, reason="END_OF_DATA")
            open_trade.exit_time = last_ts
            if open_trade.direction == Direction.LONG:
                exits_long.loc[last_ts] = True
            else:
                exits_short.loc[last_ts] = True
            trades.append(open_trade)

        return StrategyRunResult(
            entries_long=entries_long,
            entries_short=entries_short,
            exits_long=exits_long,
            exits_short=exits_short,
            stop_loss=stop_loss,
            take_profit=take_profit,
            trades=trades,
        )


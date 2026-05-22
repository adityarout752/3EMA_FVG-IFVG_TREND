"""Win/loss streak analytics for closed trade logs."""

import pandas as pd


def compute_streak_statistics(trades_df: pd.DataFrame) -> dict:
    """Compute max and average consecutive win/loss streak lengths.

    Args:
        trades_df: Closed-trade dataframe containing a `pnl` column.

    Returns:
        Dictionary with max/avg win and loss streak metrics.
    """
    if trades_df.empty:
        return {
            "max_consecutive_wins": 0,
            "max_consecutive_losses": 0,
            "avg_consecutive_wins": 0.0,
            "avg_consecutive_losses": 0.0,
        }

    outcomes = trades_df["pnl"] > 0
    win_streaks: list[int] = []
    loss_streaks: list[int] = []
    current = 0
    current_is_win = None

    for is_win in outcomes:
        if current_is_win is None:
            current_is_win = bool(is_win)
            current = 1
            continue
        if bool(is_win) == current_is_win:
            current += 1
        else:
            if current_is_win:
                win_streaks.append(current)
            else:
                loss_streaks.append(current)
            current_is_win = bool(is_win)
            current = 1

    if current_is_win is True:
        win_streaks.append(current)
    elif current_is_win is False:
        loss_streaks.append(current)

    return {
        "max_consecutive_wins": max(win_streaks) if win_streaks else 0,
        "max_consecutive_losses": max(loss_streaks) if loss_streaks else 0,
        "avg_consecutive_wins": float(sum(win_streaks) / len(win_streaks)) if win_streaks else 0.0,
        "avg_consecutive_losses": float(sum(loss_streaks) / len(loss_streaks)) if loss_streaks else 0.0,
    }


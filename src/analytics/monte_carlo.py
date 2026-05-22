"""Monte Carlo bootstrapping utilities for scenario-based robustness checks."""

import numpy as np
import pandas as pd


def bootstrap_total_return_distribution(
    trades_df: pd.DataFrame,
    n_scenarios: int = 1000,
    random_seed: int = 42,
) -> pd.DataFrame:
    """Generate Monte Carlo total-return scenarios by trade resampling.

    Args:
        trades_df: Closed-trade dataframe with a `return_pct` column.
        n_scenarios: Number of bootstrap runs.
        random_seed: RNG seed for deterministic reproducibility.

    Returns:
        Dataframe containing one total return percentage per scenario.
    """
    if trades_df.empty or "return_pct" not in trades_df:
        return pd.DataFrame(columns=["scenario", "total_return_pct"])

    rng = np.random.default_rng(random_seed)
    returns = trades_df["return_pct"].to_numpy(dtype=float)
    n = len(returns)
    results = []
    for scenario in range(n_scenarios):
        sample = rng.choice(returns, size=n, replace=True)
        total_return = (np.prod(1.0 + sample) - 1.0) * 100.0
        results.append({"scenario": scenario + 1, "total_return_pct": total_return})
    return pd.DataFrame(results)


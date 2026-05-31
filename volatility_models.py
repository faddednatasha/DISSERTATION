import numpy as np
import pandas as pd
from arch import arch_model


def compute_rolling_volatility(returns: pd.Series, window: int = 21) -> pd.Series:
    """Rolling standard deviation annualised (21-day default = ~1 month)."""
    return returns.rolling(window).std() * np.sqrt(252) * 100


def compute_garch_volatility(returns: pd.Series):
    """
    Fit symmetric GARCH(1,1) and return conditional volatility series.
    Returns (vol_series, model_summary_dict) or (None, error_str).
    """
    try:
        scaled = returns * 100
        model = arch_model(scaled.dropna(), vol="Garch", p=1, q=1, dist="normal", rescale=False)
        res = model.fit(disp="off", options={"maxiter": 500})
        cond_vol = res.conditional_volatility * np.sqrt(252)
        cond_vol.index = scaled.dropna().index
        summary = {
            "omega":  round(float(res.params["omega"]), 6),
            "alpha":  round(float(res.params["alpha[1]"]), 4),
            "beta":   round(float(res.params["beta[1]"]), 4),
            "persistence": round(float(res.params["alpha[1]"]) + float(res.params["beta[1]"]), 4),
            "aic":    round(float(res.aic), 2),
            "bic":    round(float(res.bic), 2),
            "log_likelihood": round(float(res.loglikelihood), 2),
        }
        return cond_vol, summary
    except Exception as e:
        return None, str(e)


def compute_tarch_volatility(returns: pd.Series):
    """
    Fit asymmetric TARCH(1,1,1) — GJR-GARCH.
    Captures leverage effect: bad news amplifies volatility more than good news.
    Returns (vol_series, model_summary_dict) or (None, error_str).
    """
    try:
        scaled = returns * 100
        model = arch_model(scaled.dropna(), vol="Garch", p=1, o=1, q=1, dist="normal", rescale=False)
        res = model.fit(disp="off", options={"maxiter": 500})
        cond_vol = res.conditional_volatility * np.sqrt(252)
        cond_vol.index = scaled.dropna().index

        gamma = float(res.params.get("gamma[1]", res.params.iloc[3]))
        alpha = float(res.params["alpha[1]"])
        beta  = float(res.params["beta[1]"])

        summary = {
            "omega":   round(float(res.params["omega"]), 6),
            "alpha":   round(alpha, 4),
            "gamma":   round(gamma, 4),
            "beta":    round(beta, 4),
            "persistence": round(alpha + beta + 0.5 * gamma, 4),
            "leverage_ratio": round(1 + gamma / max(alpha, 1e-8), 4),
            "aic":     round(float(res.aic), 2),
            "bic":     round(float(res.bic), 2),
            "log_likelihood": round(float(res.loglikelihood), 2),
        }
        return cond_vol, summary
    except Exception as e:
        return None, str(e)


def compute_event_impact(prices: pd.DataFrame, event_date: str, window: int = 10):
    """
    For a given event date compute:
    - Cumulative returns in [-window, +window] trading days
    - Pre vs post avg rolling volatility
    Returns a dict of impact metrics.
    """
    try:
        event_dt = pd.Timestamp(event_date)
        idx = prices.index.searchsorted(event_dt)
        if idx >= len(prices):
            return None

        pre_start  = max(0, idx - window)
        post_end   = min(len(prices), idx + window + 1)

        pre_prices  = prices.iloc[pre_start:idx]
        post_prices = prices.iloc[idx:post_end]

        if len(pre_prices) < 2 or len(post_prices) < 2:
            return None

        pre_returns  = pre_prices["Close"].pct_change().dropna()
        post_returns = post_prices["Close"].pct_change().dropna()

        pre_cum_ret  = (pre_prices["Close"].iloc[-1] / pre_prices["Close"].iloc[0] - 1) * 100
        post_cum_ret = (post_prices["Close"].iloc[-1] / post_prices["Close"].iloc[0] - 1) * 100

        event_day_ret = None
        if idx < len(prices) and idx > 0:
            event_day_ret = (prices["Close"].iloc[idx] / prices["Close"].iloc[idx - 1] - 1) * 100

        return {
            "pre_cum_return":   round(float(pre_cum_ret), 2),
            "post_cum_return":  round(float(post_cum_ret), 2),
            "event_day_return": round(float(event_day_ret), 2) if event_day_ret is not None else None,
            "pre_volatility":   round(float(pre_returns.std() * np.sqrt(252) * 100), 2),
            "post_volatility":  round(float(post_returns.std() * np.sqrt(252) * 100), 2),
            "vol_change_pct":   round(
                (post_returns.std() - pre_returns.std()) / max(pre_returns.std(), 1e-8) * 100, 2
            ),
            "window_days": window,
        }
    except Exception:
        return None

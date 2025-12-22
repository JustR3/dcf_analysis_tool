"""Portfolio Optimization Engine - Mean-Variance + Black-Litterman."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from enum import Enum
import time

import pandas as pd
import numpy as np
import yfinance as yf
from pypfopt import EfficientFrontier, risk_models, expected_returns, black_litterman
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices


class OptimizationMethod(Enum):
    """Portfolio optimization objectives."""
    MAX_SHARPE = "max_sharpe"
    MIN_VOLATILITY = "min_volatility"
    EFFICIENT_RISK = "efficient_risk"
    EQUAL_WEIGHT = "equal_weight"


@dataclass
class PortfolioMetrics:
    """Portfolio performance metrics."""
    expected_annual_return: float
    annual_volatility: float
    sharpe_ratio: float
    weights: Dict[str, float]
    optimization_method: str

    def to_dict(self) -> dict:
        return {
            "expected_annual_return": round(self.expected_annual_return, 4),
            "annual_volatility": round(self.annual_volatility, 4),
            "sharpe_ratio": round(self.sharpe_ratio, 4),
            "weights": {k: round(v, 6) for k, v in self.weights.items()},
            "optimization_method": self.optimization_method,
        }


@dataclass
class DiscretePortfolio:
    """Discrete share allocation."""
    allocation: Dict[str, int]
    leftover: float
    total_value: float

    def to_dict(self) -> dict:
        return {"allocation": self.allocation, "leftover": round(self.leftover, 2),
                "total_value": round(self.total_value, 2)}


class PortfolioEngine:
    """Portfolio optimization engine using mean-variance optimization."""

    def __init__(self, tickers: List[str], risk_free_rate: float = 0.04):
        self.tickers = [t.upper() for t in tickers]
        self.risk_free_rate = risk_free_rate
        self._last_call = 0.0
        self.prices: Optional[pd.DataFrame] = None
        self.expected_returns: Optional[pd.Series] = None
        self.cov_matrix: Optional[pd.DataFrame] = None
        self.optimized_weights: Optional[Dict[str, float]] = None
        self.performance: Optional[PortfolioMetrics] = None
        self._last_error: Optional[str] = None

    def _rate_limit(self) -> None:
        elapsed = time.time() - self._last_call
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
        self._last_call = time.time()

    def fetch_data(self, period: str = "2y", start: Optional[datetime] = None,
                   end: Optional[datetime] = None) -> bool:
        """Fetch historical price data for all tickers."""
        try:
            self._rate_limit()
            data = (yf.download(self.tickers, start=start, end=end, progress=False, auto_adjust=True)
                    if start and end else
                    yf.download(self.tickers, period=period, progress=False, auto_adjust=True))

            if data is None or data.empty:
                self._last_error = "No data returned"
                return False

            if isinstance(data.columns, pd.MultiIndex):
                self.prices = data['Close'] if isinstance(data['Close'], pd.DataFrame) else pd.DataFrame({self.tickers[0]: data['Close']})
            else:
                self.prices = data[['Close']].rename(columns={'Close': self.tickers[0]})

            self.prices = self.prices.dropna(axis=1, how='all').dropna()

            if len(self.prices) < 252:
                self._last_error = f"Insufficient data: {len(self.prices)} days"
                return False

            missing = set(self.tickers) - set(self.prices.columns)
            if missing:
                self._last_error = f"Missing: {missing}"
                return False

            return True
        except Exception as e:
            self._last_error = str(e)
            return False

    def calculate_expected_returns(self, method: str = "capm_return") -> bool:
        if self.prices is None:
            self._last_error = "No price data"
            return False
        try:
            if method == "capm_return":
                self.expected_returns = expected_returns.capm_return(self.prices)
            elif method == "ema_historical_return":
                self.expected_returns = expected_returns.ema_historical_return(self.prices)
            else:
                self.expected_returns = expected_returns.mean_historical_return(self.prices)
            return True
        except Exception as e:
            self._last_error = str(e)
            return False

    def calculate_covariance_matrix(self, method: str = "ledoit_wolf") -> bool:
        if self.prices is None:
            self._last_error = "No price data"
            return False
        try:
            if method == "ledoit_wolf":
                self.cov_matrix = risk_models.CovarianceShrinkage(self.prices).ledoit_wolf()
            elif method == "semicovariance":
                self.cov_matrix = risk_models.semicovariance(self.prices)
            else:
                self.cov_matrix = risk_models.sample_cov(self.prices)
            return True
        except Exception as e:
            self._last_error = str(e)
            return False

    def optimize(self, method: OptimizationMethod = OptimizationMethod.MAX_SHARPE,
                 target_volatility: Optional[float] = None,
                 weight_bounds: Tuple[float, float] = (0, 1)) -> Optional[PortfolioMetrics]:
        """Optimize portfolio weights."""
        try:
            if self.expected_returns is None and not self.calculate_expected_returns():
                return None
            if self.cov_matrix is None and not self.calculate_covariance_matrix():
                return None

            if method == OptimizationMethod.EQUAL_WEIGHT:
                n = len(self.tickers)
                weights = {t: 1.0 / n for t in self.tickers}
                ret = sum(weights[t] * self.expected_returns[t] for t in self.tickers)
                var = sum(sum(weights[t1] * weights[t2] * self.cov_matrix.loc[t1, t2]
                              for t2 in self.tickers) for t1 in self.tickers)
                vol = np.sqrt(var)
                self.optimized_weights = weights
                self.performance = PortfolioMetrics(ret * 100, vol * 100,
                    (ret - self.risk_free_rate) / vol, weights, method.value)
                return self.performance

            ef = EfficientFrontier(self.expected_returns, self.cov_matrix, weight_bounds=weight_bounds)

            if method == OptimizationMethod.MAX_SHARPE:
                ef.max_sharpe(risk_free_rate=self.risk_free_rate)
            elif method == OptimizationMethod.MIN_VOLATILITY:
                ef.min_volatility()
            elif method == OptimizationMethod.EFFICIENT_RISK:
                if target_volatility is None:
                    self._last_error = "target_volatility required"
                    return None
                ef.efficient_risk(target_volatility=target_volatility)

            weights = ef.clean_weights()
            perf = ef.portfolio_performance(verbose=False, risk_free_rate=self.risk_free_rate)
            self.optimized_weights = weights
            self.performance = PortfolioMetrics(perf[0] * 100, perf[1] * 100, perf[2], weights, method.value)
            return self.performance
        except Exception as e:
            self._last_error = str(e)
            return None

    def optimize_with_views(self, dcf_results: Dict[str, dict], confidence: float = 0.3,
                            method: OptimizationMethod = OptimizationMethod.MAX_SHARPE,
                            weight_bounds: Tuple[float, float] = (0, 1)) -> Optional[PortfolioMetrics]:
        """Optimize using Black-Litterman with DCF valuations as views."""
        try:
            if self.prices is None:
                self._last_error = "No price data"
                return None
            if self.expected_returns is None and not self.calculate_expected_returns():
                return None
            if self.cov_matrix is None and not self.calculate_covariance_matrix():
                return None

            # Filter to only stocks with valid DCF results (positive values)
            viewdict = {t: dcf_results[t]['upside_downside'] / 100.0
                        for t in self.tickers if t in dcf_results 
                        and dcf_results[t].get('value_per_share', 0) > 0}
            if not viewdict:
                self._last_error = "No valid DCF results with positive values"
                return None

            market_caps = pd.Series({t: dcf_results.get(t, {}).get('market_cap', 1.0)
                                     for t in viewdict.keys()})
            confidences = np.full(len(viewdict), confidence)

            bl = black_litterman.BlackLittermanModel(
                self.cov_matrix, pi="market", market_caps=market_caps,
                absolute_views=viewdict, omega="idzorek", view_confidences=confidences
            )
            bl_returns = bl.bl_returns()

            ef = EfficientFrontier(bl_returns, self.cov_matrix, weight_bounds=weight_bounds)
            try:
                if method == OptimizationMethod.MAX_SHARPE:
                    ef.max_sharpe(risk_free_rate=self.risk_free_rate)
                elif method == OptimizationMethod.MIN_VOLATILITY:
                    ef.min_volatility()
                else:
                    ef.efficient_risk(target_volatility=0.15)
            except ValueError:
                # If all returns are below risk-free rate, fall back to min volatility
                ef = EfficientFrontier(bl_returns, self.cov_matrix, weight_bounds=weight_bounds)
                ef.min_volatility()

            weights = {k: v for k, v in ef.clean_weights().items() if v > 0.001}
            perf = ef.portfolio_performance(verbose=False, risk_free_rate=self.risk_free_rate)
            self.optimized_weights = weights
            self.performance = PortfolioMetrics(
                perf[0] * 100, perf[1] * 100, perf[2], weights, f"{method.value}_black_litterman"
            )
            return self.performance
        except Exception as e:
            self._last_error = str(e)
            return None

    def get_discrete_allocation(self, total_portfolio_value: float) -> Optional[DiscretePortfolio]:
        """Calculate discrete share allocation."""
        try:
            if self.optimized_weights is None:
                self._last_error = "No optimized weights"
                return None
            self._rate_limit()
            latest = get_latest_prices(self.prices)
            da = DiscreteAllocation(self.optimized_weights, latest, total_portfolio_value=total_portfolio_value)
            allocation, leftover = da.greedy_portfolio()
            total = sum(allocation[t] * latest[t] for t in allocation)
            return DiscretePortfolio(allocation, leftover, total)
        except Exception as e:
            self._last_error = str(e)
            return None

    def get_last_error(self) -> Optional[str]:
        return self._last_error

    def to_dict(self) -> dict:
        result = {"tickers": self.tickers, "risk_free_rate": self.risk_free_rate,
                  "data_points": len(self.prices) if self.prices is not None else 0}
        if self.performance:
            result["performance"] = self.performance.to_dict()
        if self._last_error:
            result["error"] = self._last_error
        return result


def optimize_portfolio(tickers: List[str], method: OptimizationMethod = OptimizationMethod.MAX_SHARPE,
                       period: str = "2y", risk_free_rate: float = 0.04) -> Optional[PortfolioMetrics]:
    """Quick portfolio optimization."""
    engine = PortfolioEngine(tickers=tickers, risk_free_rate=risk_free_rate)
    if not engine.fetch_data(period=period):
        return None
    return engine.optimize(method=method)


def optimize_portfolio_with_dcf(dcf_results: Dict[str, dict],
                                method: OptimizationMethod = OptimizationMethod.MAX_SHARPE,
                                period: str = "2y", risk_free_rate: float = 0.04,
                                confidence: float = 0.3) -> Optional[PortfolioMetrics]:
    """Optimize portfolio using DCF valuations via Black-Litterman."""
    tickers = list(dcf_results.keys())
    if not tickers:
        return None
    engine = PortfolioEngine(tickers=tickers, risk_free_rate=risk_free_rate)
    if not engine.fetch_data(period=period):
        return None
    return engine.optimize_with_views(dcf_results=dcf_results, confidence=confidence, method=method)


def get_efficient_frontier_points(tickers: List[str], num_points: int = 100,
                                  period: str = "2y") -> Optional[pd.DataFrame]:
    """Calculate points on the efficient frontier."""
    engine = PortfolioEngine(tickers=tickers)
    if not engine.fetch_data(period=period):
        return None
    if not engine.calculate_expected_returns() or not engine.calculate_covariance_matrix():
        return None

    results = []
    targets = np.linspace(engine.expected_returns.min(), engine.expected_returns.max(), num_points)
    for target in targets:
        try:
            ef = EfficientFrontier(engine.expected_returns, engine.cov_matrix)
            ef.efficient_return(target_return=target)
            perf = ef.portfolio_performance(verbose=False, risk_free_rate=engine.risk_free_rate)
            results.append({'return': perf[0], 'volatility': perf[1], 'sharpe': perf[2]})
        except Exception:
            pass
    return pd.DataFrame(results) if results else None

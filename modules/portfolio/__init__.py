"""
Portfolio Optimization Module
==============================

Portfolio optimization engines including:
- Market Regime Detection (200-day SMA crossover)
- Mean-Variance Optimization (Markowitz) - Coming Soon
- Risk Parity - Coming Soon
- Black-Litterman Model - Coming Soon
- Fundamental-weighted portfolios using DCF valuations - Coming Soon
"""

from .regime import RegimeDetector, MarketRegime, RegimeResult

__all__ = ["RegimeDetector", "MarketRegime", "RegimeResult"]

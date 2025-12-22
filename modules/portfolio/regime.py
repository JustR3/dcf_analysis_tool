"""
RegimeDetector - Market Regime Detection Engine
================================================

Detects current market regime (RISK_ON vs RISK_OFF) using technical analysis
on SPY (S&P 500 ETF) with a 200-day Simple Moving Average crossover strategy.

Usage:
    from modules.portfolio.regime import RegimeDetector, MarketRegime
    
    detector = RegimeDetector()
    regime = detector.get_current_regime()
    
    if regime == MarketRegime.RISK_ON:
        print("Bull market detected - aggressive allocation")
    else:
        print("Bear market detected - defensive allocation")
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Callable, Optional

import pandas as pd
import yfinance as yf


# =============================================================================
# Market Regime Enum
# =============================================================================

class MarketRegime(Enum):
    """Market regime states for portfolio allocation."""
    RISK_ON = "RISK_ON"    # Bull market - price > 200-day SMA
    RISK_OFF = "RISK_OFF"  # Bear market - price < 200-day SMA
    UNKNOWN = "UNKNOWN"    # Unable to determine (data issues)

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"MarketRegime.{self.value}"


# =============================================================================
# Rate Limiter (Reused from DCF module)
# =============================================================================

class RateLimiter:
    """Rate limiter to respect yfinance API limits."""

    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.min_interval = 60 / calls_per_minute
        self.last_call = 0.0

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            elapsed = time.time() - self.last_call
            if elapsed < self.min_interval:
                time.sleep(self.min_interval - elapsed)
            self.last_call = time.time()
            return func(*args, **kwargs)
        return wrapper


# Global rate limiter
_rate_limiter = RateLimiter(calls_per_minute=60)


# =============================================================================
# Regime Detection Result
# =============================================================================

@dataclass
class RegimeResult:
    """Container for regime detection results with metadata."""
    regime: MarketRegime
    current_price: float
    sma_200: float
    signal_strength: float  # How far above/below SMA (as %)
    last_updated: datetime
    data_points: int  # Number of historical data points used
    
    def __str__(self) -> str:
        return (
            f"Regime: {self.regime.value} | "
            f"Price: ${self.current_price:.2f} | "
            f"200-SMA: ${self.sma_200:.2f} | "
            f"Signal: {self.signal_strength:+.2f}%"
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {
            "regime": self.regime.value,
            "current_price": self.current_price,
            "sma_200": self.sma_200,
            "signal_strength": self.signal_strength,
            "last_updated": self.last_updated.isoformat(),
            "data_points": self.data_points,
        }


# =============================================================================
# RegimeDetector Class
# =============================================================================

class RegimeDetector:
    """
    Market Regime Detector using 200-day SMA crossover on SPY.
    
    This class fetches historical SPY data and determines the current market
    regime (RISK_ON/RISK_OFF) based on price position relative to 200-day SMA.
    
    Methodology:
        - RISK_ON (Bull): Current price > 200-day SMA
        - RISK_OFF (Bear): Current price < 200-day SMA
        
    The 200-day SMA is a widely-used technical indicator for long-term trends.
    
    Attributes:
        ticker: Market index ticker (default: "SPY")
        lookback_days: Historical data period (default: 300 days for 200-day SMA)
        cache_duration: How long to cache results in seconds (default: 3600)
        
    Example:
        >>> detector = RegimeDetector()
        >>> result = detector.get_current_regime()
        >>> print(result.regime)
        MarketRegime.RISK_ON
        
        >>> # Check if bullish
        >>> if detector.is_risk_on():
        ...     print("Bullish market - increase equity allocation")
        
        >>> # Get detailed information
        >>> result = detector.get_regime_with_details()
        >>> print(f"Signal strength: {result.signal_strength:.2f}%")
    """

    def __init__(
        self,
        ticker: str = "SPY",
        lookback_days: int = 300,
        cache_duration: int = 3600
    ):
        """
        Initialize RegimeDetector.
        
        Args:
            ticker: Market index ticker symbol (default: SPY for S&P 500)
            lookback_days: Days of historical data to fetch (default: 300)
            cache_duration: Cache validity period in seconds (default: 1 hour)
        """
        self.ticker = ticker.upper()
        self.lookback_days = lookback_days
        self.cache_duration = cache_duration
        
        # Cache for regime results
        self._cached_result: Optional[RegimeResult] = None
        self._cache_timestamp: Optional[datetime] = None
        self._last_error: Optional[str] = None

    @property
    def last_error(self) -> Optional[str]:
        """Get last error message if detection failed."""
        return self._last_error

    def _is_cache_valid(self) -> bool:
        """Check if cached result is still valid."""
        if self._cached_result is None or self._cache_timestamp is None:
            return False
        
        elapsed = (datetime.now() - self._cache_timestamp).total_seconds()
        return elapsed < self.cache_duration

    @_rate_limiter
    def _fetch_spy_data(self) -> Optional[pd.DataFrame]:
        """
        Fetch historical SPY data from yfinance.
        
        Returns:
            DataFrame with OHLCV data, or None if fetch fails
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=self.lookback_days)
            
            spy = yf.Ticker(self.ticker)
            data = spy.history(start=start_date, end=end_date)
            
            if data.empty:
                self._last_error = f"No data returned for {self.ticker}"
                return None
            
            self._last_error = None
            return data
            
        except Exception as e:
            self._last_error = f"Error fetching {self.ticker} data: {str(e)}"
            return None

    def _calculate_regime(self, data: pd.DataFrame) -> Optional[RegimeResult]:
        """
        Calculate market regime from historical data.
        
        Args:
            data: DataFrame with Close prices
            
        Returns:
            RegimeResult with detection details, or None if calculation fails
        """
        try:
            # Ensure we have enough data for 200-day SMA
            if len(data) < 200:
                self._last_error = (
                    f"Insufficient data: {len(data)} days "
                    f"(need at least 200 for SMA calculation)"
                )
                return None
            
            # Calculate 200-day Simple Moving Average
            sma_200 = data['Close'].rolling(window=200).mean()
            
            # Get current (most recent) values
            current_price = float(data['Close'].iloc[-1])
            current_sma = float(sma_200.iloc[-1])
            
            # Determine regime based on crossover
            if current_price > current_sma:
                regime = MarketRegime.RISK_ON
            else:
                regime = MarketRegime.RISK_OFF
            
            # Calculate signal strength (% above/below SMA)
            signal_strength = ((current_price - current_sma) / current_sma) * 100
            
            result = RegimeResult(
                regime=regime,
                current_price=current_price,
                sma_200=current_sma,
                signal_strength=signal_strength,
                last_updated=datetime.now(),
                data_points=len(data),
            )
            
            self._last_error = None
            return result
            
        except Exception as e:
            self._last_error = f"Error calculating regime: {str(e)}"
            return None

    def get_regime_with_details(self, use_cache: bool = True) -> Optional[RegimeResult]:
        """
        Get current market regime with detailed information.
        
        Args:
            use_cache: If True, return cached result if still valid
            
        Returns:
            RegimeResult with full details, or None if detection fails
        """
        # Return cached result if valid
        if use_cache and self._is_cache_valid():
            return self._cached_result
        
        # Fetch fresh data
        data = self._fetch_spy_data()
        if data is None:
            return None
        
        # Calculate regime
        result = self._calculate_regime(data)
        
        # Update cache
        if result is not None:
            self._cached_result = result
            self._cache_timestamp = datetime.now()
        
        return result

    def get_current_regime(self, use_cache: bool = True) -> MarketRegime:
        """
        Get current market regime (simplified API).
        
        Args:
            use_cache: If True, return cached result if still valid
            
        Returns:
            MarketRegime enum (RISK_ON, RISK_OFF, or UNKNOWN on error)
        """
        result = self.get_regime_with_details(use_cache=use_cache)
        
        if result is None:
            return MarketRegime.UNKNOWN
        
        return result.regime

    def is_risk_on(self, use_cache: bool = True) -> bool:
        """
        Check if current regime is RISK_ON (bull market).
        
        Args:
            use_cache: If True, use cached result if still valid
            
        Returns:
            True if RISK_ON, False otherwise
        """
        regime = self.get_current_regime(use_cache=use_cache)
        return regime == MarketRegime.RISK_ON

    def is_risk_off(self, use_cache: bool = True) -> bool:
        """
        Check if current regime is RISK_OFF (bear market).
        
        Args:
            use_cache: If True, use cached result if still valid
            
        Returns:
            True if RISK_OFF, False otherwise
        """
        regime = self.get_current_regime(use_cache=use_cache)
        return regime == MarketRegime.RISK_OFF

    def get_signal_strength(self, use_cache: bool = True) -> Optional[float]:
        """
        Get signal strength (% distance from 200-day SMA).
        
        Positive values indicate price above SMA (bullish).
        Negative values indicate price below SMA (bearish).
        
        Args:
            use_cache: If True, use cached result if still valid
            
        Returns:
            Signal strength as percentage, or None if detection fails
        """
        result = self.get_regime_with_details(use_cache=use_cache)
        
        if result is None:
            return None
        
        return result.signal_strength

    def to_dict(self, use_cache: bool = True) -> Optional[dict]:
        """
        Export regime detection results as dictionary.
        
        Args:
            use_cache: If True, use cached result if still valid
            
        Returns:
            Dictionary with regime data, or None if detection fails
        """
        result = self.get_regime_with_details(use_cache=use_cache)
        
        if result is None:
            return None
        
        return result.to_dict()

    def clear_cache(self) -> None:
        """Clear cached regime data to force fresh calculation."""
        self._cached_result = None
        self._cache_timestamp = None


# =============================================================================
# Convenience Functions
# =============================================================================

def get_market_regime(use_cache: bool = True) -> MarketRegime:
    """
    Quick function to get current market regime.
    
    Args:
        use_cache: If True, use cached result if available
        
    Returns:
        MarketRegime enum
        
    Example:
        >>> regime = get_market_regime()
        >>> if regime == MarketRegime.RISK_ON:
        ...     print("Bull market!")
    """
    detector = RegimeDetector()
    return detector.get_current_regime(use_cache=use_cache)


def is_bull_market(use_cache: bool = True) -> bool:
    """
    Quick check if market is in RISK_ON regime.
    
    Args:
        use_cache: If True, use cached result if available
        
    Returns:
        True if bull market (RISK_ON), False otherwise
    """
    detector = RegimeDetector()
    return detector.is_risk_on(use_cache=use_cache)


def is_bear_market(use_cache: bool = True) -> bool:
    """
    Quick check if market is in RISK_OFF regime.
    
    Args:
        use_cache: If True, use cached result if available
        
    Returns:
        True if bear market (RISK_OFF), False otherwise
    """
    detector = RegimeDetector()
    return detector.is_risk_off(use_cache=use_cache)

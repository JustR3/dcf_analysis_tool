"""
Shiller CAPE (Cyclically Adjusted PE) Loader
Macro God: Robert Shiller's market valuation signal

Downloads and parses Shiller's U.S. stock market data including CAPE ratio.
Provides macro-level market valuation signals for portfolio risk adjustment.
"""

import pandas as pd
import requests
from typing import Optional, Dict
from pathlib import Path
import io
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.utils import default_cache, retry_with_backoff


# Shiller data URL (official source)
SHILLER_DATA_URL = "https://www.econ.yale.edu/~shiller/data/ie_data.xls"


def download_shiller_data() -> Optional[pd.DataFrame]:
    """
    Download Shiller's CAPE data from Yale.
    
    Returns:
        DataFrame with columns: Date, Price, Dividend, Earnings, CPI, 
                                Long_Rate, Real_Price, Real_Dividend, 
                                Real_Earnings, CAPE, etc.
    """
    print("📊 Downloading Shiller CAPE data from Yale...")
    
    def fetch():
        try:
            response = requests.get(SHILLER_DATA_URL, timeout=30)
            response.raise_for_status()
            
            # Parse Excel file
            # Shiller's file has data starting around row 7
            df = pd.read_excel(io.BytesIO(response.content), sheet_name='Data', header=7)
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            # The file has fractional year dates (e.g., 1871.01 = Jan 1871)
            # Keep first ~15 columns which are the main data
            df = df.iloc[:, :15]
            
            # Rename key columns for clarity
            col_map = {}
            for col in df.columns:
                col_str = str(col).lower()
                if 'date' in col_str or df.columns.tolist().index(col) == 0:
                    col_map[col] = 'Date'
                elif 'p' == col_str or 's&p' in col_str:
                    col_map[col] = 'Price'
                elif 'd' == col_str or 'dividend' in col_str:
                    col_map[col] = 'Dividend'
                elif 'e' == col_str or 'earnings' in col_str:
                    col_map[col] = 'Earnings'
                elif 'cpi' in col_str:
                    col_map[col] = 'CPI'
                elif 'cape' in col_str or 'p/e10' in col_str or 'cyclically' in col_str:
                    col_map[col] = 'CAPE'
                elif 'tr' in col_str or 'total return' in col_str:
                    col_map[col] = 'Total_Return_Price'
            
            if col_map:
                df = df.rename(columns=col_map)
            
            # Drop rows with missing Date
            df = df.dropna(subset=['Date'])
            
            # Convert Date to datetime (fractional year to period)
            # 1871.01 -> Jan 1871
            df['Year'] = df['Date'].astype(float).apply(lambda x: int(x))
            df['Month'] = df['Date'].astype(float).apply(lambda x: int((x % 1) * 12) + 1)
            df['Date'] = pd.to_datetime(df[['Year', 'Month']].assign(day=1))
            
            # Keep only relevant columns
            keep_cols = ['Date', 'Price', 'Dividend', 'Earnings', 'CPI', 'CAPE']
            keep_cols = [c for c in keep_cols if c in df.columns]
            df = df[keep_cols]
            
            # Drop rows where all data is missing
            df = df.dropna(how='all', subset=[c for c in df.columns if c != 'Date'])
            
            return df
            
        except Exception as e:
            print(f"  ⚠️  Error downloading Shiller data: {e}")
            return None
    
    result = retry_with_backoff(fetch, max_attempts=3)
    
    if result is not None:
        print(f"✅ Downloaded {len(result)} months of Shiller data")
        return result
    else:
        print("❌ Failed to download Shiller data")
        return None


def get_shiller_data(use_cache: bool = True, cache_expiry_hours: int = 168) -> Optional[pd.DataFrame]:
    """
    Get Shiller CAPE data with caching.
    
    Args:
        use_cache: Whether to use cached data (default: True)
        cache_expiry_hours: Cache freshness in hours (default: 168 = 1 week)
    
    Returns:
        DataFrame with Shiller data or None if failed
    """
    cache_key = "shiller_cape_data"
    
    # Try cache first
    if use_cache:
        cached = default_cache.get(cache_key, expiry_hours=cache_expiry_hours)
        if cached is not None:
            print(f"✅ Loaded Shiller data from cache ({len(cached)} rows)")
            return cached
    
    # Download fresh data
    df = download_shiller_data()
    
    if df is not None:
        # Cache it
        default_cache.set(cache_key, df)
    
    return df


def get_current_cape() -> Optional[float]:
    """
    Get the most recent CAPE ratio.
    
    Returns:
        Current CAPE value or None if data unavailable
    """
    df = get_shiller_data()
    
    if df is None or 'CAPE' not in df.columns:
        return None
    
    # Get most recent non-null CAPE
    cape_series = df['CAPE'].dropna()
    
    if cape_series.empty:
        return None
    
    return float(cape_series.iloc[-1])


def get_cape_history(months: int = 120) -> Optional[pd.DataFrame]:
    """
    Get historical CAPE data for the last N months.
    
    Args:
        months: Number of months of history (default: 120 = 10 years)
    
    Returns:
        DataFrame with Date and CAPE columns
    """
    df = get_shiller_data()
    
    if df is None:
        return None
    
    # Filter to last N months
    df = df.tail(months).copy()
    
    return df[['Date', 'CAPE']].dropna()


def get_equity_risk_scalar(
    cape_low: float = 15.0,
    cape_high: float = 35.0,
    scalar_low: float = 1.2,
    scalar_high: float = 0.7
) -> Dict:
    """
    Calculate equity risk adjustment scalar based on CAPE.
    
    Logic:
        - CAPE < cape_low: Market is cheap → increase expected returns (scalar > 1)
        - CAPE > cape_high: Market is expensive → decrease expected returns (scalar < 1)
        - Linear interpolation between thresholds
    
    Args:
        cape_low: CAPE threshold for "cheap" market (default: 15)
        cape_high: CAPE threshold for "expensive" market (default: 35)
        scalar_low: Return multiplier when CAPE is low (default: 1.2 = +20%)
        scalar_high: Return multiplier when CAPE is high (default: 0.7 = -30%)
    
    Returns:
        Dictionary with:
            - current_cape: Current CAPE value
            - risk_scalar: Adjustment factor for expected returns
            - regime: "CHEAP", "FAIR", "EXPENSIVE"
            - description: Human-readable description
    """
    cape = get_current_cape()
    
    if cape is None:
        # Fallback to neutral if no data
        return {
            'current_cape': None,
            'risk_scalar': 1.0,
            'regime': 'UNKNOWN',
            'description': 'CAPE data unavailable, using neutral adjustment'
        }
    
    # Calculate scalar using linear interpolation
    if cape <= cape_low:
        scalar = scalar_low
        regime = 'CHEAP'
    elif cape >= cape_high:
        scalar = scalar_high
        regime = 'EXPENSIVE'
    else:
        # Linear interpolation between thresholds
        fraction = (cape - cape_low) / (cape_high - cape_low)
        scalar = scalar_low + fraction * (scalar_high - scalar_low)
        regime = 'FAIR'
    
    # Generate description
    pct_change = (scalar - 1.0) * 100
    if scalar > 1.0:
        desc = f"Market valuation attractive (CAPE={cape:.1f}). Increasing expected returns by {pct_change:+.1f}%"
    elif scalar < 1.0:
        desc = f"Market valuation elevated (CAPE={cape:.1f}). Reducing expected returns by {pct_change:+.1f}%"
    else:
        desc = f"Market valuation fair (CAPE={cape:.1f}). No adjustment"
    
    return {
        'current_cape': cape,
        'risk_scalar': scalar,
        'regime': regime,
        'description': desc
    }


def display_cape_summary(cape_data: Optional[dict] = None):
    """Display a formatted summary of current CAPE valuation.
    
    Args:
        cape_data: Optional dict from get_equity_risk_scalar(). If None, will fetch fresh data.
    """
    
    print("\n" + "=" * 80)
    print("📊 SHILLER CAPE VALUATION SUMMARY")
    print("=" * 80 + "\n")
    
    # Use provided data or fetch fresh
    if cape_data is None:
        cape = get_current_cape()
        
        if cape is None:
            print("❌ CAPE data unavailable")
            return
        
        print(f"Current CAPE Ratio: {cape:.2f}")
        print()
        
        # Historical context
        df = get_shiller_data()
        if df is not None and 'CAPE' in df.columns:
            cape_series = df['CAPE'].dropna()
            
            mean_cape = cape_series.mean()
            median_cape = cape_series.median()
            percentile = (cape_series < cape).sum() / len(cape_series) * 100
            
            print(f"Historical Context:")
            print(f"  Mean CAPE (all-time):      {mean_cape:.2f}")
            print(f"  Median CAPE (all-time):    {median_cape:.2f}")
            print(f"  Current Percentile:        {percentile:.1f}%")
            print()
        
        # Get risk scalar
        try:
            cape_data = get_equity_risk_scalar()
        except Exception:
            print("❌ Could not calculate risk scalar")
            return
    
    # Display formatted output
    if cape_data and isinstance(cape_data, dict):
        print(f"Current CAPE: {cape_data.get('current_cape', 'N/A')}")
        print(f"Regime: {cape_data.get('regime', 'N/A')}")
        print(f"Risk Scalar: {cape_data.get('risk_scalar', 1.0):.2f}x")
        print(f"Description: {cape_data.get('description', 'N/A')}")
        
        # Show percentile if available
        if 'percentile' in cape_data:
            print(f"Percentile: {cape_data['percentile']:.1f}%")
    
    print("\n" + "=" * 80 + "\n")
    scalar_info = get_equity_risk_scalar()
    
    print(f"Macro Regime: {scalar_info['regime']}")
    print(f"Risk Scalar:  {scalar_info['risk_scalar']:.2f}x")
    print(f"Interpretation: {scalar_info['description']}")
    print()
    
    # 10-year range
    history = get_cape_history(months=120)
    if history is not None:
        recent_min = history['CAPE'].min()
        recent_max = history['CAPE'].max()
        print(f"10-Year Range: [{recent_min:.2f}, {recent_max:.2f}]")
    
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    """Test the Shiller CAPE loader."""
    
    print("\n" + "=" * 80)
    print("🧪 SHILLER CAPE LOADER TEST")
    print("=" * 80 + "\n")
    
    # Test 1: Download and parse data
    df = get_shiller_data(use_cache=False)
    
    if df is not None:
        print(f"✅ Successfully loaded {len(df)} rows")
        print(f"   Date range: {df['Date'].min()} to {df['Date'].max()}")
        print(f"   Columns: {list(df.columns)}")
        print()
        
        # Show recent data
        print("Recent CAPE values:")
        print(df[['Date', 'CAPE']].tail(10))
        print()
    
    # Test 2: Get current CAPE
    cape = get_current_cape()
    print(f"Current CAPE: {cape}")
    print()
    
    # Test 3: Get risk scalar
    scalar_info = get_equity_risk_scalar()
    print(f"Risk Scalar: {scalar_info}")
    print()
    
    # Test 4: Display summary
    display_cape_summary()

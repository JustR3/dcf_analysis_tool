#!/usr/bin/env python3
"""Quick test for the full pipeline: DCF → Portfolio Optimization."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.valuation import DCFEngine
from modules.portfolio import PortfolioEngine, RegimeDetector, OptimizationMethod


def main():
    print("=" * 60)
    print("  Full Pipeline Test")
    print("=" * 60)
    
    # Test tickers
    tickers = ["AAPL", "MSFT", "GOOGL", "NVDA"]
    
    # Step 1: DCF Valuations
    print("\n1. DCF Valuations")
    print("-" * 60)
    
    dcf_results = {}
    for ticker in tickers:
        engine = DCFEngine(ticker, auto_fetch=True)
        if engine.is_ready:
            result = engine.get_intrinsic_value()  # Use analyst estimates
            dcf_results[ticker] = result
            upside = result['upside_downside']
            status = "🟢" if upside > 20 else "🔴" if upside < -20 else "🟡"
            print(f"  {ticker}: ${result['value_per_share']:.2f} ({upside:+.1f}%) {status}")
        else:
            print(f"  {ticker}: ❌ {engine.last_error}")
    
    if len(dcf_results) < 2:
        print("Not enough valid stocks")
        return
    
    # Step 2: Market Regime
    print("\n2. Market Regime")
    print("-" * 60)
    
    detector = RegimeDetector()
    regime = detector.get_current_regime()
    print(f"  Regime: {regime}")
    
    # Step 3: Portfolio Optimization
    print("\n3. Portfolio Optimization (Black-Litterman)")
    print("-" * 60)
    
    engine = PortfolioEngine(list(dcf_results.keys()))
    if not engine.fetch_data(period="2y"):
        print(f"  Error: {engine.get_last_error()}")
        return
    
    result = engine.optimize_with_views(dcf_results, confidence=0.3)
    if result:
        print(f"  Expected Return: {result.expected_annual_return:.2f}%")
        print(f"  Volatility: {result.annual_volatility:.2f}%")
        print(f"  Sharpe Ratio: {result.sharpe_ratio:.2f}")
        print("\n  Weights:")
        for ticker, weight in sorted(result.weights.items(), key=lambda x: x[1], reverse=True):
            print(f"    {ticker}: {weight*100:.1f}%")
    else:
        print(f"  Error: {engine.get_last_error()}")
    
    # Step 4: Discrete Allocation
    print("\n4. Discrete Allocation ($100,000)")
    print("-" * 60)
    
    alloc = engine.get_discrete_allocation(100000)
    if alloc:
        for ticker, shares in alloc.allocation.items():
            value = shares * dcf_results[ticker]['current_price']
            print(f"  {ticker}: {shares} shares (${value:,.0f})")
        print(f"\n  Total Invested: ${alloc.total_value:,.2f}")
        print(f"  Leftover Cash: ${alloc.leftover:,.2f}")
    
    print("\n" + "=" * 60)
    print("  ✓ Pipeline Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()

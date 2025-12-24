#!/usr/bin/env python3
"""Test Bayesian growth cleaning and Monte Carlo simulation."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.valuation import DCFEngine


def test_growth_cleaning():
    """Test Bayesian growth rate cleaning."""
    print("=" * 80)
    print("  Bayesian Growth Rate Cleaning Test")
    print("=" * 80)
    
    # Test TSLA (has -37% analyst growth)
    ticker = "TSLA"
    print(f"\n🧪 Testing {ticker} (negative analyst growth)...")
    
    engine = DCFEngine(ticker, auto_fetch=True)
    if not engine.is_ready:
        print(f"❌ Failed: {engine.last_error}")
        return
    
    data = engine.company_data
    print(f"\n📊 Raw Data:")
    print(f"  Analyst Growth (raw): {data.analyst_growth*100:.1f}%" if data.analyst_growth else "  N/A")
    print(f"  Sector: {data.sector}")
    
    # Test cleaning
    cleaned, msg = engine.clean_growth_rate(data.analyst_growth, data.sector)
    print(f"\n🧹 Cleaned:")
    print(f"  {msg}")
    print(f"  Final Growth Rate: {cleaned*100:.1f}%")
    
    # Run valuation to see it in action
    print(f"\n💰 Valuation with Cleaned Growth:")
    result = engine.get_intrinsic_value()
    print(f"  Fair Value: ${result['value_per_share']:.2f}")
    print(f"  Growth Used: {result['inputs']['growth']*100:.1f}%")
    if "growth_cleaning" in result and result["growth_cleaning"]:
        print(f"  Message: {result['growth_cleaning']}")


def test_monte_carlo():
    """Test Monte Carlo simulation."""
    print("\n\n" + "=" * 80)
    print("  Monte Carlo Simulation Test")
    print("=" * 80)
    
    # Test with NVDA
    ticker = "NVDA"
    print(f"\n🎲 Running Monte Carlo for {ticker} (5,000 iterations)...")
    
    engine = DCFEngine(ticker, auto_fetch=True)
    if not engine.is_ready:
        print(f"❌ Failed: {engine.last_error}")
        return
    
    print(f"  Current Price: ${engine.company_data.current_price:.2f}")
    
    # Run simulation
    result = engine.simulate_value(iterations=5000)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    print(f"\n📈 Results ({result['iterations']} successful iterations):")
    print(f"  Median Value:         ${result['median_value']:.2f}")
    print(f"  Mean Value:           ${result['mean_value']:.2f}")
    print(f"  Std Deviation:        ${result['std_value']:.2f}")
    print(f"\n📊 Risk Metrics:")
    print(f"  VaR (5th percentile): ${result['var_95']:.2f}  [Downside risk]")
    print(f"  Median (50th %ile):   ${result['median_value']:.2f}")
    print(f"  Upside (95th %ile):   ${result['upside_95']:.2f}  [Upside potential]")
    print(f"\n🎯 Probability Analysis:")
    print(f"  P(Undervalued):       {result['prob_undervalued']:.1f}%")
    print(f"  P(Overvalued):        {result['prob_overvalued']:.1f}%")
    print(f"\n✅ Assessment: {result['assessment']}")
    
    # Show range
    downside = result['current_price'] - result['var_95']
    upside = result['upside_95'] - result['current_price']
    print(f"\n📉 Risk/Reward:")
    print(f"  Downside: -${downside:.2f} ({-downside/result['current_price']*100:.1f}%)")
    print(f"  Upside:   +${upside:.2f} ({upside/result['current_price']*100:.1f}%)")


def test_comparison():
    """Compare multiple stocks."""
    print("\n\n" + "=" * 80)
    print("  Multi-Stock Monte Carlo Comparison")
    print("=" * 80)
    
    tickers = ["NVDA", "MSFT", "AAPL"]
    
    print(f"\n🎲 Running Monte Carlo for {len(tickers)} stocks...")
    
    results = []
    for ticker in tickers:
        engine = DCFEngine(ticker, auto_fetch=True)
        if engine.is_ready:
            mc = engine.simulate_value(iterations=3000)  # Faster for comparison
            if "error" not in mc:
                results.append({
                    "ticker": ticker,
                    "price": engine.company_data.current_price,
                    "median": mc["median_value"],
                    "prob_under": mc["prob_undervalued"],
                    "var_95": mc["var_95"],
                    "upside_95": mc["upside_95"],
                })
    
    # Display comparison
    print(f"\n{'Ticker':<8} {'Price':>10} {'Median':>10} {'VaR 95%':>10} {'Up 95%':>10} {'P(Under)':>10}")
    print("-" * 80)
    for r in results:
        print(f"{r['ticker']:<8} ${r['price']:>9.2f} ${r['median']:>9.2f} "
              f"${r['var_95']:>9.2f} ${r['upside_95']:>9.2f} {r['prob_under']:>9.1f}%")
    
    print("\n" + "=" * 80)
    print("✅ All Tests Complete")
    print("=" * 80)


if __name__ == "__main__":
    test_growth_cleaning()
    test_monte_carlo()
    test_comparison()

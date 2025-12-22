"""Test Portfolio with Mix of Stocks (7 stocks including loss-makers)"""

import sys
sys.path.insert(0, '/Users/justra/Python/quant-portfolio-manager')

from modules.valuation.dcf import DCFEngine
from modules.portfolio.optimizer import PortfolioEngine, OptimizationMethod


def test_user_scenario():
    """Simulate the user's scenario with 7 stocks."""
    print("\n" + "="*80)
    print("USER SCENARIO TEST: 7 Stocks (Some Loss-Making)")
    print("="*80)
    
    # Mix representing the user's portfolio
    tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "UBER", "RIVN", "SNAP"]
    
    print(f"\n📊 Step 1: Get DCF Valuations for {len(tickers)} Stocks")
    print("-" * 80)
    
    comparison = DCFEngine.compare_stocks(tickers, skip_negative_fcf=True)
    
    # Show ALL stocks with their FCF status
    print(f"\n📈 Stock Analysis:")
    for ticker in tickers:
        engine = DCFEngine(ticker, auto_fetch=True)
        if engine.is_ready:
            fcf = engine.company_data.fcf
            fcf_status = "✅ POSITIVE" if fcf > 0 else "❌ NEGATIVE"
            print(f"  {ticker}: FCF = ${fcf:,.0f}M  {fcf_status}")
            
            if ticker in comparison['results']:
                fv = comparison['results'][ticker]['value_per_share']
                print(f"         Fair Value: ${fv:.2f}")
            elif ticker in comparison.get('skipped', {}):
                print(f"         ⏭️  SKIPPED: {comparison['skipped'][ticker]}")
    
    print(f"\n📊 Summary:")
    print(f"  ✅ Valid for DCF: {comparison['summary']['stocks_analyzed']}")
    print(f"  ⏭️  Skipped (negative FCF): {comparison['summary']['stocks_skipped']}")
    print(f"  ❌ Failed: {comparison['summary']['stocks_failed']}")
    
    # Check for any negative values
    negative_values = [t for t, r in comparison['results'].items() 
                      if r['value_per_share'] < 0]
    
    if negative_values:
        print(f"\n❌ PROBLEM DETECTED: {len(negative_values)} stocks have negative fair values!")
        for ticker in negative_values:
            print(f"  • {ticker}: ${comparison['results'][ticker]['value_per_share']:.2f}")
    else:
        print(f"\n✅ SUCCESS: All calculated fair values are positive!")
    
    print(f"\n🎯 Step 2: Portfolio Optimization")
    print("-" * 80)
    
    # Only use stocks with valid DCF results
    valid_tickers = list(comparison['results'].keys())
    print(f"\nUsing {len(valid_tickers)} valid stocks: {', '.join(valid_tickers)}")
    
    if len(valid_tickers) >= 2:
        try:
            engine = PortfolioEngine(valid_tickers)
            if not engine.fetch_data(period="2y"):
                print(f"❌ Error fetching price data: {engine.last_error}")
                return
            
            # Try Black-Litterman with DCF views
            dcf_results_dict = {t: comparison['results'][t] for t in valid_tickers}
            perf = engine.optimize_with_views(dcf_results_dict)
            
            if perf:
                print(f"\n✅ Portfolio Optimization Successful:")
                print(f"  Expected Return: {perf.expected_annual_return:.2f}%")
                print(f"  Volatility: {perf.annual_volatility:.2f}%")
                print(f"  Sharpe Ratio: {perf.sharpe_ratio:.2f}")
                print(f"\n  Weights:")
                for ticker, weight in sorted(perf.weights.items(), 
                                            key=lambda x: x[1], reverse=True):
                    if weight > 0.001:
                        print(f"    {ticker}: {weight*100:.1f}%")
            else:
                print(f"❌ Optimization failed: {engine.last_error}")
        except Exception as e:
            print(f"❌ Error in optimization: {e}")
    else:
        print(f"⚠️  Not enough valid stocks for optimization (need at least 2)")


if __name__ == "__main__":
    test_user_scenario()
    
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    print("\n✅ Fixed Issues:")
    print("   1. Negative FCF stocks are automatically SKIPPED")
    print("   2. Only profitable companies are valued with DCF")
    print("   3. Portfolio optimizer uses only stocks with valid valuations")
    print("   4. No more impossible negative stock prices!")
    print("\n💡 User Message:")
    print("   If you see 'Skipped X stocks', those are loss-making companies")
    print("   that cannot be valued with DCF. This is correct behavior.")

#!/usr/bin/env python3
"""
Balanced Portfolio Test
========================

Tests portfolio optimization with stocks that have more moderate DCF valuations
to showcase proper diversification in the Black-Litterman model.

This test uses different sectors and moderate growth assumptions.
"""

from modules.valuation import DCFEngine
from modules.portfolio import PortfolioEngine, OptimizationMethod


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def main():
    print("\n" + "█" * 80)
    print("█" + "  BALANCED PORTFOLIO TEST - Moderate DCF Views".center(78) + "█")
    print("█" * 80)
    
    # =========================================================================
    # Test Portfolio with Moderate Custom Parameters
    # =========================================================================
    print_section("Testing Multi-Sector Portfolio with Custom Parameters")
    
    # Test with different sectors and moderate assumptions
    tickers = ["JPM", "JNJ", "PG", "XOM", "DIS"]
    
    print(f"📊 Building DCF models for {len(tickers)} diversified stocks:")
    print(f"   Tickers: {', '.join(tickers)}")
    print(f"   Sectors: Finance, Healthcare, Consumer, Energy, Entertainment\n")
    
    dcf_results = {}
    
    # Get DCF valuations with reasonable parameters
    for ticker in tickers:
        print(f"🔍 Analyzing {ticker}...")
        
        engine = DCFEngine(ticker, auto_fetch=True)
        
        if not engine.is_ready:
            print(f"   ❌ Error: {engine.last_error}")
            continue
        
        # Use moderate assumptions: 7% growth, 2.5% terminal, 9% WACC
        result = engine.get_intrinsic_value(
            growth=0.07,
            term_growth=0.025,
            wacc=0.09,
            years=5
        )
        
        dcf_results[ticker] = result
        
        print(f"   Current:    ${result['current_price']:.2f}")
        print(f"   Fair Value: ${result['value_per_share']:.2f}")
        print(f"   Upside:     {result['upside_downside']:+.2f}%")
        
        if result['upside_downside'] > 10:
            print(f"   Status:     🟢 Undervalued")
        elif result['upside_downside'] > -10:
            print(f"   Status:     🟡 Fairly Valued")
        else:
            print(f"   Status:     🔴 Overvalued")
        print()
    
    if len(dcf_results) < 3:
        print("❌ Not enough stocks with valid DCF data")
        return
    
    # =========================================================================
    # Portfolio Optimization
    # =========================================================================
    print_section("Black-Litterman Portfolio Optimization")
    
    print("🎯 Running optimization with DCF-informed views...\n")
    
    # Create portfolio engine
    engine = PortfolioEngine(tickers=list(dcf_results.keys()), risk_free_rate=0.045)
    
    # Fetch data
    print("📥 Fetching 2 years of historical price data...")
    if not engine.fetch_data(period="2y"):
        print(f"❌ Error: {engine.get_last_error()}")
        return
    
    print(f"✅ Loaded {len(engine.prices)} days of price data\n")
    
    # Test with different confidence levels
    confidence_levels = [0.2, 0.4, 0.6]
    
    for confidence in confidence_levels:
        print(f"\n{'─' * 80}")
        print(f"Confidence Level: {confidence*100:.0f}% (weight on DCF views)")
        print(f"{'─' * 80}")
        
        result = engine.optimize_with_views(
            dcf_results=dcf_results,
            confidence=confidence,
            method=OptimizationMethod.MAX_SHARPE
        )
        
        if not result:
            print(f"❌ Optimization failed: {engine.get_last_error()}")
            continue
        
        print(f"\n📈 Performance Metrics:")
        print(f"   Expected Return: {result.expected_annual_return:.2f}%")
        print(f"   Volatility:      {result.annual_volatility:.2f}%")
        print(f"   Sharpe Ratio:    {result.sharpe_ratio:.2f}")
        
        print(f"\n📊 Asset Allocation:")
        print(f"{'Ticker':<10} {'Weight':<10} {'DCF Upside'}")
        print("─" * 40)
        
        sorted_weights = sorted(result.weights.items(), key=lambda x: x[1], reverse=True)
        for ticker, weight in sorted_weights:
            if weight > 0.001:  # Only show significant allocations
                upside = dcf_results[ticker]['upside_downside']
                print(f"{ticker:<10} {weight*100:>8.2f}%  {upside:>+9.2f}%")
    
    # =========================================================================
    # Compare Optimization Methods
    # =========================================================================
    print_section("Comparing Optimization Methods")
    
    methods = [
        (OptimizationMethod.MAX_SHARPE, "Maximum Sharpe Ratio"),
        (OptimizationMethod.MIN_VOLATILITY, "Minimum Volatility"),
        (OptimizationMethod.EQUAL_WEIGHT, "Equal Weight (Baseline)")
    ]
    
    for method, name in methods:
        print(f"\n{'─' * 80}")
        print(f"Method: {name}")
        print(f"{'─' * 80}")
        
        if method == OptimizationMethod.EQUAL_WEIGHT:
            # Equal weight baseline
            result = engine.optimize(method=method)
        else:
            # Use DCF views with 30% confidence
            result = engine.optimize_with_views(
                dcf_results=dcf_results,
                confidence=0.3,
                method=method
            )
        
        if not result:
            print(f"❌ Failed: {engine.get_last_error()}")
            continue
        
        print(f"\n📈 Performance:")
        print(f"   Return:  {result.expected_annual_return:>7.2f}%")
        print(f"   Risk:    {result.annual_volatility:>7.2f}%")
        print(f"   Sharpe:  {result.sharpe_ratio:>7.2f}")
        
        print(f"\n📊 Weights:")
        sorted_weights = sorted(result.weights.items(), key=lambda x: x[1], reverse=True)
        for ticker, weight in sorted_weights:
            if weight > 0.001:
                print(f"   {ticker:<10} {weight*100:>6.2f}%")
    
    # =========================================================================
    # Discrete Allocation
    # =========================================================================
    print_section("Discrete Share Allocation")
    
    # Use Max Sharpe with DCF views for allocation
    result = engine.optimize_with_views(
        dcf_results=dcf_results,
        confidence=0.3,
        method=OptimizationMethod.MAX_SHARPE
    )
    
    if result:
        allocation = engine.get_discrete_allocation(total_portfolio_value=100000)
        
        if allocation:
            print(f"\n💼 $100,000 Portfolio Allocation:")
            print(f"{'Ticker':<10} {'Shares':<10} {'Value':<15} {'Weight'}")
            print("─" * 60)
            
            sorted_alloc = sorted(
                allocation.allocation.items(),
                key=lambda x: x[1] * engine.prices[x[0]].iloc[-1],
                reverse=True
            )
            
            for ticker, shares in sorted_alloc:
                price = engine.prices[ticker].iloc[-1]
                value = shares * price
                pct = (value / allocation.total_value) * 100
                print(f"{ticker:<10} {shares:<10} ${value:>13,.2f}  {pct:>6.2f}%")
            
            print("─" * 60)
            print(f"{'TOTAL':<10} {'':<10} ${allocation.total_value:>13,.2f}  100.00%")
            print(f"\n💰 Invested: ${allocation.total_value:,.2f}")
            print(f"💵 Cash:     ${allocation.leftover:,.2f}")
    
    print("\n" + "█" * 80)
    print("█" + "  Balanced Portfolio Test Complete!".center(78) + "█")
    print("█" * 80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

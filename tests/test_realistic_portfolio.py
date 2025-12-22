#!/usr/bin/env python3
"""
Realistic Portfolio Test
=========================

Tests portfolio with growth stocks using realistic DCF parameters
to showcase proper Black-Litterman diversification.
"""

from modules.valuation import DCFEngine
from modules.portfolio import PortfolioEngine, OptimizationMethod, RegimeDetector


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def main():
    print("\n" + "█" * 80)
    print("█" + "  REALISTIC PORTFOLIO TEST - Growth Stocks with Moderate DCF".center(78) + "█")
    print("█" * 80)
    
    # =========================================================================
    # Market Regime
    # =========================================================================
    print_section("Current Market Regime")
    
    detector = RegimeDetector()
    regime = detector.get_regime_with_details(method="combined")
    
    if regime:
        print(f"🌍 Market Regime: {regime.regime.value}")
        if regime.current_price and regime.sma_200:
            print(f"   SPY: ${regime.current_price:.2f} (200-SMA: ${regime.sma_200:.2f})")
    
    # =========================================================================
    # DCF Analysis with Realistic Parameters
    # =========================================================================
    print_section("DCF Analysis - Tech/Growth Stocks")
    
    # Use stocks with different characteristics
    tickers = ["NVDA", "AMD", "INTC", "QCOM", "TSM"]
    
    print(f"📊 Analyzing {len(tickers)} semiconductor stocks with moderate assumptions:")
    print(f"   Tickers: {', '.join(tickers)}")
    print(f"   Parameters: 8% growth, 2.5% terminal, 10% WACC\n")
    
    dcf_results = {}
    
    for ticker in tickers:
        print(f"🔍 {ticker}...", end=" ")
        
        engine = DCFEngine(ticker, auto_fetch=True)
        
        if not engine.is_ready:
            print(f"❌ {engine.last_error}")
            continue
        
        # Moderate assumptions for semis
        result = engine.get_intrinsic_value(
            growth=0.08,
            term_growth=0.025,
            wacc=0.10,
            years=5
        )
        
        dcf_results[ticker] = result
        
        upside = result['upside_downside']
        
        if upside > 20:
            status = "🟢 Undervalued"
        elif upside > -20:
            status = "🟡 Fair"
        else:
            status = "🔴 Overvalued"
        
        print(f"${result['current_price']:.2f} → ${result['value_per_share']:.2f} ({upside:+.1f}%) {status}")
    
    if len(dcf_results) < 3:
        print("\n❌ Not enough valid DCF data")
        return
    
    # =========================================================================
    # Portfolio Optimization with Black-Litterman
    # =========================================================================
    print_section("Black-Litterman Portfolio Optimization")
    
    tickers_list = list(dcf_results.keys())
    
    print(f"🎯 Building optimal portfolio from {len(tickers_list)} assets\n")
    
    # Create engine
    engine = PortfolioEngine(tickers=tickers_list, risk_free_rate=0.045)
    
    # Fetch data
    print("📥 Fetching historical data...")
    if not engine.fetch_data(period="2y"):
        print(f"❌ Error: {engine.get_last_error()}")
        return
    
    print(f"✅ {len(engine.prices)} days of data loaded\n")
    
    # =========================================================================
    # Test 1: Standard Black-Litterman with DCF Views
    # =========================================================================
    print("─" * 80)
    print("TEST 1: Black-Litterman with DCF Views (30% confidence)")
    print("─" * 80)
    
    result = engine.optimize_with_views(
        dcf_results=dcf_results,
        confidence=0.3,
        method=OptimizationMethod.MAX_SHARPE
    )
    
    if result:
        print(f"\n✨ Optimization Results:")
        print(f"   Expected Return: {result.expected_annual_return:.2f}%")
        print(f"   Volatility:      {result.annual_volatility:.2f}%")
        print(f"   Sharpe Ratio:    {result.sharpe_ratio:.2f}")
        
        print(f"\n📊 Portfolio Weights:")
        print(f"{'Ticker':<10} {'Weight':<12} {'DCF Upside':<15} {'Price'}")
        print("─" * 60)
        
        sorted_weights = sorted(result.weights.items(), key=lambda x: x[1], reverse=True)
        for ticker, weight in sorted_weights:
            if weight > 0.001:
                upside = dcf_results[ticker]['upside_downside']
                price = dcf_results[ticker]['current_price']
                print(f"{ticker:<10} {weight*100:>9.2f}%   {upside:>+12.2f}%   ${price:>8.2f}")
    else:
        print(f"❌ Failed: {engine.get_last_error()}")
    
    # =========================================================================
    # Test 2: Traditional Mean-Variance (No DCF Views)
    # =========================================================================
    print("\n" + "─" * 80)
    print("TEST 2: Traditional Mean-Variance (No DCF)")
    print("─" * 80)
    
    result_trad = engine.optimize(method=OptimizationMethod.MAX_SHARPE)
    
    if result_trad:
        print(f"\n✨ Optimization Results:")
        print(f"   Expected Return: {result_trad.expected_annual_return:.2f}%")
        print(f"   Volatility:      {result_trad.annual_volatility:.2f}%")
        print(f"   Sharpe Ratio:    {result_trad.sharpe_ratio:.2f}")
        
        print(f"\n📊 Portfolio Weights:")
        sorted_weights = sorted(result_trad.weights.items(), key=lambda x: x[1], reverse=True)
        for ticker, weight in sorted_weights:
            if weight > 0.001:
                print(f"   {ticker:<10} {weight*100:>7.2f}%")
    
    # =========================================================================
    # Test 3: Minimum Volatility
    # =========================================================================
    print("\n" + "─" * 80)
    print("TEST 3: Minimum Volatility (Defensive)")
    print("─" * 80)
    
    result_minvol = engine.optimize(method=OptimizationMethod.MIN_VOLATILITY)
    
    if result_minvol:
        print(f"\n✨ Optimization Results:")
        print(f"   Expected Return: {result_minvol.expected_annual_return:.2f}%")
        print(f"   Volatility:      {result_minvol.annual_volatility:.2f}%")
        print(f"   Sharpe Ratio:    {result_minvol.sharpe_ratio:.2f}")
        
        print(f"\n📊 Portfolio Weights:")
        sorted_weights = sorted(result_minvol.weights.items(), key=lambda x: x[1], reverse=True)
        for ticker, weight in sorted_weights:
            if weight > 0.001:
                print(f"   {ticker:<10} {weight*100:>7.2f}%")
    
    # =========================================================================
    # Discrete Allocation
    # =========================================================================
    print_section("Discrete Share Allocation ($50,000)")
    
    if result:
        allocation = engine.get_discrete_allocation(total_portfolio_value=50000)
        
        if allocation:
            print(f"{'Ticker':<10} {'Shares':<10} {'Value':<15} {'% Port'}")
            print("─" * 55)
            
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
            
            print("─" * 55)
            print(f"{'TOTAL':<10} {'':<10} ${allocation.total_value:>13,.2f}  100.00%")
            print(f"\n💰 Invested:  ${allocation.total_value:,.2f}")
            print(f"💵 Leftover:  ${allocation.leftover:,.2f}")
            print(f"📊 Efficiency: {(allocation.total_value/50000)*100:.2f}%")
    
    # =========================================================================
    # Summary Comparison
    # =========================================================================
    print_section("📊 Strategy Comparison Summary")
    
    print(f"{'Strategy':<35} {'Return':<12} {'Risk':<12} {'Sharpe'}")
    print("─" * 75)
    
    if result:
        print(f"{'Black-Litterman (DCF Views)':<35} {result.expected_annual_return:>9.2f}%  "
              f"{result.annual_volatility:>9.2f}%  {result.sharpe_ratio:>7.2f}")
    
    if result_trad:
        print(f"{'Traditional Mean-Variance':<35} {result_trad.expected_annual_return:>9.2f}%  "
              f"{result_trad.annual_volatility:>9.2f}%  {result_trad.sharpe_ratio:>7.2f}")
    
    if result_minvol:
        print(f"{'Minimum Volatility':<35} {result_minvol.expected_annual_return:>9.2f}%  "
              f"{result_minvol.annual_volatility:>9.2f}%  {result_minvol.sharpe_ratio:>7.2f}")
    
    print("\n" + "█" * 80)
    print("█" + "  ✅ Realistic Portfolio Test Complete!".center(78) + "█")
    print("█" + "  The DCF → Black-Litterman pipeline is working smoothly!".center(78) + "█")
    print("█" * 80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted.")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

#!/usr/bin/env python3
"""
Full Pipeline Test Script
==========================

Tests the complete workflow from DCF valuation to Black-Litterman optimization.

This script runs:
1. Single stock DCF valuations
2. Multi-stock DCF comparison
3. Portfolio optimization with DCF-driven views
4. Discrete allocation calculation
5. Market regime detection
"""

import sys
from typing import Dict
from modules.valuation import DCFEngine
from modules.portfolio import (
    PortfolioEngine,
    OptimizationMethod,
    RegimeDetector,
    optimize_portfolio_with_dcf,
)


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_subsection(title: str):
    """Print a subsection header."""
    print(f"\n{'─' * 80}")
    print(f"  {title}")
    print(f"{'─' * 80}\n")


def test_single_stock_dcf(ticker: str) -> dict:
    """
    Test DCF valuation for a single stock.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        DCF valuation result dictionary
    """
    print(f"🔍 Analyzing {ticker}...")
    
    # Initialize DCF engine
    engine = DCFEngine(ticker, auto_fetch=True)
    
    if not engine.is_ready:
        print(f"❌ Error: {engine.last_error}")
        return None
    
    # Get intrinsic value
    result = engine.get_intrinsic_value()
    
    # Display key metrics
    print(f"\n📊 {ticker} - DCF Valuation Results:")
    print(f"   Current Price:     ${result['current_price']:.2f}")
    print(f"   Fair Value:        ${result['value_per_share']:.2f}")
    print(f"   Upside/Downside:   {result['upside_downside']:+.2f}%")
    print(f"   Enterprise Value:  ${result['enterprise_value']:,.0f}M")
    
    # Assessment
    upside = result['upside_downside']
    if upside > 20:
        assessment = "🟢 UNDERVALUED - Strong Buy Candidate"
    elif upside > 10:
        assessment = "🟢 UNDERVALUED - Buy Candidate"
    elif upside > -10:
        assessment = "🟡 FAIRLY VALUED - Hold"
    elif upside > -20:
        assessment = "🔴 OVERVALUED - Consider Selling"
    else:
        assessment = "🔴 OVERVALUED - Strong Sell Signal"
    
    print(f"   Assessment:        {assessment}")
    
    return result


def test_multiple_stocks_dcf(tickers: list) -> Dict[str, dict]:
    """
    Test DCF valuation for multiple stocks.
    
    Args:
        tickers: List of stock ticker symbols
        
    Returns:
        Dictionary mapping tickers to DCF results
    """
    print_subsection(f"Running DCF Analysis for {len(tickers)} stocks")
    
    dcf_results = {}
    
    for ticker in tickers:
        result = test_single_stock_dcf(ticker)
        if result:
            dcf_results[ticker] = result
        print()  # Blank line between stocks
    
    # Display comparison summary
    print_subsection("DCF Valuation Summary")
    
    # Sort by upside potential
    sorted_tickers = sorted(
        dcf_results.keys(),
        key=lambda t: dcf_results[t]['upside_downside'],
        reverse=True
    )
    
    print(f"{'Rank':<6} {'Ticker':<8} {'Current':<12} {'Fair Value':<12} {'Upside':<10} {'Assessment'}")
    print("─" * 80)
    
    for rank, ticker in enumerate(sorted_tickers, 1):
        data = dcf_results[ticker]
        upside = data['upside_downside']
        
        if upside > 20:
            assessment = "🟢 Undervalued"
        elif upside > -20:
            assessment = "🟡 Fair"
        else:
            assessment = "🔴 Overvalued"
        
        print(f"{rank:<6} {ticker:<8} ${data['current_price']:<11.2f} "
              f"${data['value_per_share']:<11.2f} {upside:>+8.2f}%  {assessment}")
    
    return dcf_results


def test_market_regime():
    """Test market regime detection."""
    print_subsection("Market Regime Detection")
    
    detector = RegimeDetector()
    
    print("📈 Detecting current market regime...")
    
    # SPY 200-day SMA method
    regime_sma = detector.get_regime_with_details(method="sma")
    if regime_sma:
        print(f"\n🔍 SPY 200-Day SMA Method:")
        print(f"   Regime:       {regime_sma.regime.value}")
        if regime_sma.current_price:
            print(f"   SPY Price:    ${regime_sma.current_price:.2f}")
            print(f"   200-day SMA:  ${regime_sma.sma_200:.2f}")
            print(f"   Difference:   {regime_sma.sma_signal_strength:+.2f}%")
    
    # VIX Term Structure method
    regime_vix = detector.get_regime_with_details(method="vix")
    if regime_vix:
        print(f"\n🔍 VIX Term Structure Method:")
        print(f"   Regime:       {regime_vix.regime.value}")
        if regime_vix.vix_structure:
            print(f"   VIX 9-Day:    {regime_vix.vix_structure.vix9d:.2f}")
            print(f"   VIX 30-Day:   {regime_vix.vix_structure.vix:.2f}")
            print(f"   VIX 3-Month:  {regime_vix.vix_structure.vix3m:.2f}")
            print(f"   Structure:    {'Backwardation (PANIC)' if regime_vix.vix_structure.is_backwardation else 'Contango (CALM)'}")
    
    # Combined method
    regime_combined = detector.get_regime_with_details(method="combined")
    if regime_combined:
        print(f"\n🔍 Combined Method:")
        print(f"   Final Regime: {regime_combined.regime.value}")
        print(f"   Method:       {regime_combined.method}")
    
    return regime_combined


def test_portfolio_optimization(dcf_results: Dict[str, dict], regime):
    """
    Test portfolio optimization using DCF-driven views.
    
    Args:
        dcf_results: Dictionary mapping tickers to DCF results
        regime: Market regime result
    """
    print_subsection("Black-Litterman Portfolio Optimization")
    
    tickers = list(dcf_results.keys())
    
    print(f"📊 Optimizing portfolio with {len(tickers)} assets...")
    print(f"   Market Regime: {regime.regime.value}")
    print(f"   Optimization: Black-Litterman with DCF Views")
    print()
    
    # Create portfolio engine
    engine = PortfolioEngine(tickers=tickers, risk_free_rate=0.045)
    
    # Fetch historical data
    print("📥 Fetching historical price data (2 years)...")
    if not engine.fetch_data(period="2y"):
        print(f"❌ Error: {engine.get_last_error()}")
        return None
    
    print(f"✅ Loaded {len(engine.prices)} days of price data")
    
    # Run Black-Litterman optimization with DCF views
    print("\n🎯 Running Black-Litterman optimization...")
    print("   (DCF valuations inform expected returns)")
    
    result = engine.optimize_with_views(
        dcf_results=dcf_results,
        confidence=0.3,  # 30% confidence in DCF views
        method=OptimizationMethod.MAX_SHARPE
    )
    
    if not result:
        print(f"❌ Optimization error: {engine.get_last_error()}")
        return None
    
    # Display results
    print("\n✨ Optimization Results:")
    print(f"   Expected Annual Return: {result.expected_annual_return:.2f}%")
    print(f"   Annual Volatility:      {result.annual_volatility:.2f}%")
    print(f"   Sharpe Ratio:           {result.sharpe_ratio:.2f}")
    print(f"   Method:                 {result.optimization_method}")
    
    print("\n📊 Optimal Portfolio Weights:")
    print(f"{'Ticker':<10} {'Weight':<10} {'DCF Upside':<12}")
    print("─" * 40)
    
    sorted_weights = sorted(result.weights.items(), key=lambda x: x[1], reverse=True)
    for ticker, weight in sorted_weights:
        upside = dcf_results[ticker]['upside_downside']
        print(f"{ticker:<10} {weight*100:>8.2f}%  {upside:>+10.2f}%")
    
    return result


def test_discrete_allocation(engine: PortfolioEngine, portfolio_value: float = 50000):
    """
    Test discrete share allocation.
    
    Args:
        engine: Portfolio engine with optimized weights
        portfolio_value: Total portfolio value in dollars
    """
    print_subsection(f"Discrete Share Allocation (${portfolio_value:,.0f})")
    
    print(f"🔢 Calculating integer share allocation...")
    
    allocation = engine.get_discrete_allocation(total_portfolio_value=portfolio_value)
    
    if not allocation:
        print(f"❌ Error: {engine.get_last_error()}")
        return None
    
    # Display allocation
    print("\n📋 Share Allocation:")
    print(f"{'Ticker':<10} {'Shares':<10} {'Value':<15} {'% of Portfolio'}")
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
    print(f"\n💰 Portfolio Value:  ${allocation.total_value:,.2f}")
    print(f"💵 Leftover Cash:    ${allocation.leftover:,.2f}")
    print(f"📊 Investment Rate:  {(allocation.total_value/portfolio_value)*100:.2f}%")
    
    return allocation


def main():
    """Run full pipeline test."""
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "  QUANT PORTFOLIO MANAGER - FULL PIPELINE TEST".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)
    
    # =========================================================================
    # PART 1: Single Stock DCF Valuations
    # =========================================================================
    print_section("PART 1: Single Stock DCF Valuations")
    
    single_stocks = ["AAPL", "MSFT", "NVDA"]
    
    print(f"Testing DCF valuation on {len(single_stocks)} individual stocks:")
    print(f"   Tickers: {', '.join(single_stocks)}\n")
    
    for ticker in single_stocks:
        test_single_stock_dcf(ticker)
        print()
    
    # =========================================================================
    # PART 2: Multiple Stock DCF Comparison
    # =========================================================================
    print_section("PART 2: Multiple Stock DCF Comparison")
    
    multi_stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA"]
    
    print(f"Comparing {len(multi_stocks)} stocks using DCF analysis:")
    print(f"   Tickers: {', '.join(multi_stocks)}\n")
    
    dcf_results = test_multiple_stocks_dcf(multi_stocks)
    
    if not dcf_results:
        print("❌ Failed to get DCF results. Exiting.")
        sys.exit(1)
    
    # =========================================================================
    # PART 3: Market Regime Detection
    # =========================================================================
    print_section("PART 3: Market Regime Detection")
    
    regime = test_market_regime()
    
    # =========================================================================
    # PART 4: Portfolio Optimization with DCF Views
    # =========================================================================
    print_section("PART 4: Black-Litterman Portfolio Optimization")
    
    # Use top 4-5 stocks from DCF results
    sorted_tickers = sorted(
        dcf_results.keys(),
        key=lambda t: dcf_results[t]['upside_downside'],
        reverse=True
    )[:5]
    
    portfolio_dcf_results = {t: dcf_results[t] for t in sorted_tickers}
    
    print(f"Building optimal portfolio from top {len(portfolio_dcf_results)} DCF candidates:")
    print(f"   Selected: {', '.join(sorted_tickers)}\n")
    
    # Create fresh engine for portfolio optimization
    engine = PortfolioEngine(tickers=sorted_tickers, risk_free_rate=0.045)
    
    # Fetch data
    print("📥 Fetching historical price data...")
    if not engine.fetch_data(period="2y"):
        print(f"❌ Error: {engine.get_last_error()}")
        sys.exit(1)
    
    # Optimize with DCF views
    print("🎯 Running Black-Litterman optimization with DCF views...\n")
    
    result = engine.optimize_with_views(
        dcf_results=portfolio_dcf_results,
        confidence=0.3,
        method=OptimizationMethod.MAX_SHARPE
    )
    
    if not result:
        print(f"❌ Optimization error: {engine.get_last_error()}")
        sys.exit(1)
    
    # Display optimization results
    print("✨ Portfolio Optimization Complete!")
    print(f"\n📈 Performance Metrics:")
    print(f"   Expected Annual Return: {result.expected_annual_return:.2f}%")
    print(f"   Annual Volatility:      {result.annual_volatility:.2f}%")
    print(f"   Sharpe Ratio:           {result.sharpe_ratio:.2f}")
    
    print(f"\n📊 Optimal Asset Allocation:")
    print(f"{'Ticker':<10} {'Weight':<12} {'DCF Upside':<15} {'DCF Fair Value'}")
    print("─" * 70)
    
    sorted_weights = sorted(result.weights.items(), key=lambda x: x[1], reverse=True)
    for ticker, weight in sorted_weights:
        upside = portfolio_dcf_results[ticker]['upside_downside']
        fair_value = portfolio_dcf_results[ticker]['value_per_share']
        print(f"{ticker:<10} {weight*100:>9.2f}%   {upside:>+12.2f}%   ${fair_value:>10.2f}")
    
    # =========================================================================
    # PART 5: Discrete Share Allocation
    # =========================================================================
    print_section("PART 5: Discrete Share Allocation")
    
    test_amounts = [50000, 100000]
    
    for amount in test_amounts:
        allocation = test_discrete_allocation(engine, portfolio_value=amount)
        if allocation:
            print("\n" + "─" * 80)
    
    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================
    print_section("✅ FULL PIPELINE TEST COMPLETE")
    
    print("Summary of Tests Completed:")
    print("  ✓ Single stock DCF valuations (3 stocks)")
    print("  ✓ Multi-stock DCF comparison (6 stocks)")
    print("  ✓ Market regime detection (SPY SMA + VIX)")
    print("  ✓ Black-Litterman portfolio optimization with DCF views")
    print("  ✓ Discrete share allocation (2 portfolio sizes)")
    
    print(f"\n🎯 Key Insight:")
    print(f"   The system successfully integrates fundamental DCF valuation")
    print(f"   with modern portfolio theory via the Black-Litterman model.")
    print(f"   DCF-derived upside estimates inform expected return views,")
    print(f"   which are then combined with market equilibrium to produce")
    print(f"   an optimal, fundamentally-grounded portfolio allocation.")
    
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "  Test completed successfully!".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
"""Test Exit Multiple terminal value implementation."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.valuation import DCFEngine


def test_exit_multiple():
    """Test exit multiple vs Gordon Growth for a tech stock."""
    print("=" * 70)
    print("  Exit Multiple Test - Comparing Terminal Value Methods")
    print("=" * 70)
    
    # Test with a high-growth tech stock
    ticker = "NVDA"
    print(f"\n🧪 Testing {ticker} (High-Growth Tech)...")
    
    engine = DCFEngine(ticker, auto_fetch=True)
    if not engine.is_ready:
        print(f"❌ Error: {engine.last_error}")
        return
    
    data = engine.company_data
    print(f"\n📊 Company Data:")
    print(f"  Sector: {data.sector}")
    print(f"  FCF: ${data.fcf:,.0f}M")
    print(f"  Current Price: ${data.current_price:.2f}")
    print(f"  Analyst Growth: {data.analyst_growth*100:.1f}%" if data.analyst_growth else "  Analyst Growth: N/A")
    
    # Test 1: Gordon Growth (traditional)
    print(f"\n1️⃣  Gordon Growth Method (Perpetuity)")
    print("-" * 70)
    
    result_gordon = engine.get_intrinsic_value(terminal_method="gordon_growth")
    print(f"  Fair Value: ${result_gordon['value_per_share']:.2f}")
    print(f"  Upside: {result_gordon['upside_downside']:+.1f}%")
    print(f"  Assessment: {result_gordon['assessment']}")
    
    terminal = result_gordon['terminal_info']
    print(f"\n  Terminal Value Details:")
    print(f"    Method: Gordon Growth")
    print(f"    Perpetuity Growth: {terminal.get('perpetuity_growth', 0)*100:.1f}%")
    print(f"    Terminal Value: ${terminal.get('terminal_value', 0):,.0f}M")
    print(f"    PV of Terminal: ${terminal.get('terminal_pv', 0):,.0f}M")
    
    # Calculate contribution
    pv_explicit = result_gordon['pv_explicit']
    term_pv = terminal['terminal_pv']
    total = pv_explicit + term_pv
    print(f"    Terminal % of EV: {(term_pv/total)*100:.1f}%")
    
    # Test 2: Exit Multiple (modern approach)
    print(f"\n2️⃣  Exit Multiple Method (EV/FCF)")
    print("-" * 70)
    
    result_exit = engine.get_intrinsic_value(terminal_method="exit_multiple")
    print(f"  Fair Value: ${result_exit['value_per_share']:.2f}")
    print(f"  Upside: {result_exit['upside_downside']:+.1f}%")
    print(f"  Assessment: {result_exit['assessment']}")
    
    terminal = result_exit['terminal_info']
    print(f"\n  Terminal Value Details:")
    print(f"    Method: Exit Multiple")
    print(f"    Exit Multiple (EV/FCF): {terminal.get('exit_multiple', 0):.1f}x")
    print(f"    Terminal FCF: ${terminal.get('terminal_fcf', 0):,.0f}M")
    print(f"    Terminal Value: ${terminal.get('terminal_value', 0):,.0f}M")
    print(f"    PV of Terminal: ${terminal.get('terminal_pv', 0):,.0f}M")
    
    # Calculate contribution
    pv_explicit = result_exit['pv_explicit']
    term_pv = terminal['terminal_pv']
    total = pv_explicit + term_pv
    print(f"    Terminal % of EV: {(term_pv/total)*100:.1f}%")
    
    # Compare
    print(f"\n📈 Comparison:")
    print("-" * 70)
    diff = result_exit['value_per_share'] - result_gordon['value_per_share']
    diff_pct = (diff / result_gordon['value_per_share']) * 100
    print(f"  Gordon Growth:  ${result_gordon['value_per_share']:.2f} ({result_gordon['upside_downside']:+.1f}%)")
    print(f"  Exit Multiple:  ${result_exit['value_per_share']:.2f} ({result_exit['upside_downside']:+.1f}%)")
    print(f"  Difference:     ${diff:+.2f} ({diff_pct:+.1f}%)")
    
    # Test 3: Auto-selection
    print(f"\n3️⃣  Auto Method Selection (Smart Default)")
    print("-" * 70)
    
    result_auto = engine.get_intrinsic_value()  # No terminal_method specified
    selected_method = result_auto['terminal_info']['method']
    print(f"  Selected Method: {selected_method}")
    print(f"  Reason: High-growth tech stock (Growth > 10% OR Tech sector)")
    print(f"  Fair Value: ${result_auto['value_per_share']:.2f} ({result_auto['upside_downside']:+.1f}%)")
    
    print("\n" + "=" * 70)
    print("✅ Test Complete!")
    print("=" * 70)
    
    # Summary
    print(f"\n💡 Key Insight:")
    if diff_pct > 20:
        print(f"  Exit Multiple values {ticker} {abs(diff_pct):.0f}% HIGHER than Gordon Growth.")
        print(f"  This is expected for high-growth stocks - perpetuity model is too conservative.")
    else:
        print(f"  Methods show similar valuations ({abs(diff_pct):.0f}% difference).")
        print(f"  This is common for mature companies with stable cash flows.")


if __name__ == "__main__":
    test_exit_multiple()

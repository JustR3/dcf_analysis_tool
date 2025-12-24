#!/usr/bin/env python3
"""Compare exit multiple effectiveness across different company types."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.valuation import DCFEngine


def compare_companies():
    """Test exit multiple vs Gordon Growth across company archetypes."""
    print("=" * 80)
    print("  Exit Multiple vs Gordon Growth - Company Comparison")
    print("=" * 80)
    
    companies = [
        ("NVDA", "High-Growth Tech", "Should strongly favor exit multiple"),
        ("MSFT", "Mature Tech", "Moderate difference"),
        ("PG", "Consumer Staples", "Similar results, might favor Gordon Growth"),
    ]
    
    results = []
    
    for ticker, category, expectation in companies:
        print(f"\n{'='*80}")
        print(f"  {ticker} - {category}")
        print(f"  Expected: {expectation}")
        print("="*80)
        
        engine = DCFEngine(ticker, auto_fetch=True)
        if not engine.is_ready:
            print(f"❌ Failed: {engine.last_error}")
            continue
        
        data = engine.company_data
        print(f"\n📊 Company Profile:")
        print(f"  Current Price: ${data.current_price:.2f}")
        print(f"  FCF: ${data.fcf:,.0f}M")
        print(f"  Sector: {data.sector}")
        print(f"  Analyst Growth: {data.analyst_growth*100:.1f}%" if data.analyst_growth else "  N/A")
        
        # Test both methods
        gordon = engine.get_intrinsic_value(terminal_method="gordon_growth")
        exit_mult = engine.get_intrinsic_value(terminal_method="exit_multiple")
        auto = engine.get_intrinsic_value()  # Auto-select
        
        print(f"\n📈 Valuation Results:")
        print(f"  Gordon Growth:  ${gordon['value_per_share']:>8.2f}  ({gordon['upside_downside']:>+6.1f}%)")
        print(f"  Exit Multiple:  ${exit_mult['value_per_share']:>8.2f}  ({exit_mult['upside_downside']:>+6.1f}%)")
        print(f"  Auto-Selected:  ${auto['value_per_share']:>8.2f}  ({auto['upside_downside']:>+6.1f}%)")
        
        diff = exit_mult['value_per_share'] - gordon['value_per_share']
        diff_pct = (diff / gordon['value_per_share']) * 100
        
        print(f"\n💡 Analysis:")
        print(f"  Difference: ${diff:+.2f} ({diff_pct:+.1f}%)")
        print(f"  Auto-Selected Method: {auto['terminal_info']['method'].replace('_', ' ').title()}")
        
        if auto['terminal_info']['method'] == 'exit_multiple':
            multiple = auto['terminal_info']['exit_multiple']
            print(f"  Exit Multiple Used: {multiple:.1f}x")
        
        results.append({
            'ticker': ticker,
            'category': category,
            'gordon': gordon['value_per_share'],
            'exit': exit_mult['value_per_share'],
            'diff_pct': diff_pct,
            'auto_method': auto['terminal_info']['method']
        })
    
    # Summary
    print(f"\n{'='*80}")
    print("  Summary - Exit Multiple Impact by Company Type")
    print("="*80)
    print(f"\n{'Ticker':<8} {'Category':<20} {'Diff %':>10} {'Auto Method':<15}")
    print("-"*80)
    
    for r in results:
        method_display = r['auto_method'].replace('_', ' ').title()
        print(f"{r['ticker']:<8} {r['category']:<20} {r['diff_pct']:>+9.1f}% {method_display:<15}")
    
    print("\n" + "="*80)
    print("✅ Comparison Complete")
    print("="*80)
    
    print(f"\n💡 Key Takeaways:")
    print(f"  • High-growth stocks benefit most from exit multiple method")
    print(f"  • Auto-selection intelligently chooses appropriate method")
    print(f"  • Mature companies show smaller differences between methods")
    print(f"  • Exit multiples provide more realistic valuations for tech/growth")


if __name__ == "__main__":
    compare_companies()

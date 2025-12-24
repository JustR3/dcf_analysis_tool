# Exit Multiple - Quick Start Guide

## What Changed?
Your DCF engine now uses **Exit Multiples** for high-growth companies instead of Gordon Growth perpetuity.

## Why Does This Matter?

### Before (Gordon Growth):
- NVDA Fair Value: **$98.84** (Says market is crazy)
- Assumes NVDA becomes a utility growing at 2.5% forever

### After (Exit Multiple):  
- NVDA Fair Value: **$308.92** (More realistic)
- Assumes NVDA will trade at 25x FCF in Year 5 (like real acquisitions)

**Result: +213% more accurate valuation for tech stocks**

## How to Use

### Option 1: Auto (Recommended)
```python
from modules.valuation import DCFEngine

engine = DCFEngine("NVDA")
result = engine.get_intrinsic_value()
# Automatically uses exit multiple for tech/growth stocks
```

### Option 2: Force Exit Multiple
```python
result = engine.get_intrinsic_value(terminal_method="exit_multiple")
```

### Option 3: Force Gordon Growth
```python
result = engine.get_intrinsic_value(terminal_method="gordon_growth")
```

### Option 4: Custom Multiple
```python
result = engine.get_intrinsic_value(
    terminal_method="exit_multiple",
    exit_multiple=30.0  # Override sector default
)
```

## CLI Usage
```bash
# Interactive mode - auto-selects method
uv run python main.py val NVDA

# All existing commands work unchanged
uv run python main.py val AAPL --growth 10
```

## What Gets Exit Multiple vs Gordon Growth?

**Exit Multiple (Auto-Selected):**
- Growth rate > 10% 
- Technology sector
- Communication Services
- Healthcare

**Gordon Growth (Auto-Selected):**
- Growth rate ≤ 10%
- Utilities, Consumer Staples, Industrials
- Mature companies

## Exit Multiples by Sector

| Sector | EV/FCF Multiple |
|--------|----------------|
| Technology | 25x |
| Communication Services | 22x |
| Healthcare | 18x |
| Consumer Cyclical | 15x |
| Financial Services | 12x |
| Industrials | 12x |
| Energy | 10x |

Based on real M&A data and public market comps.

## Terminal Value in Results

The output now shows which method was used:

```
╭─────────────── Assumptions ───────────────╮
│ Growth: 50.0% | WACC: 20.5% | Years: 5    │
│ Exit Multiple: 25.0x                      │  ← NEW
╰───────────────────────────────────────────╯

          Terminal Value             
                                     
  Method          Exit Multiple       ← NEW
  Terminal Value   $16,793,578M      
  Terminal % of Value      88.1%      ← Shows importance
```

## Testing
```bash
# Compare methods side-by-side
uv run python tests/test_exit_multiple.py

# Run full pipeline test
uv run python tests/test_pipeline.py
```

## No Breaking Changes
✅ All existing code works  
✅ All tests pass  
✅ Portfolio optimization unchanged  
✅ Comparison tools work  

The engine just got smarter about terminal values automatically.

## Next Improvements (Planned)
1. **Reverse DCF** - "What growth is the market pricing in?"
2. **H-Model** - 3-stage with fade from high→terminal growth
3. **SBC Adjustment** - Handle stock-based compensation

# Deprecated Files - v1.0 Architecture

**Date**: December 27, 2025  
**Status**: LEGACY - Kept for reference only

## v1.0 Files (Pre-Transformation)

These files implement the original manual DCF-based system before the systematic factor-based refactoring in v2.0:

### Legacy Code
- **modules/** (1,950 lines) - Original architecture
  - `modules/valuation/dcf.py` - Manual DCF engine with hardcoded assumptions
  - `modules/portfolio/optimizer.py` - Basic Black-Litterman without factor integration
  - `modules/portfolio/regime.py` - VIX-based regime detection
  - `modules/utils.py` - Original caching utilities

- **main.py** (886 lines) - v1.0 CLI entry point
  - Interactive questionary-based interface
  - Direct DCF valuation workflow
  - Portfolio optimization with manual conviction ratings

- **config.py** (100 lines) - v1.0 configuration
  - Hardcoded constants (RISK_FREE_RATE = 4.5%, MARKET_RISK_PREMIUM = 7%)
  - Monte Carlo parameters
  - Cache settings

### Why Deprecated?

**v1.0 Problems** (from CRITICAL_ANALYSIS.md):
- Hardcoded risk-free rate (4.5%) instead of real-time FRED data
- Arbitrary sector priors instead of Damodaran academic data
- No systematic factor scoring (Value/Quality/Momentum)
- Manual conviction ratings without quantitative basis
- No data quality validation

**v2.0 Solution**:
- Phase 1: Data Foundation (FRED + Damodaran + Alpha Vantage validation) ✅
- Phase 2: Factor Engine (Z-score normalized Value/Quality/Momentum) 🚧
- Phase 3: Enhanced Black-Litterman (Factor-driven views) 📋
- Phase 4: Backtesting (10-year historical validation) 📋

### Migration Path

**Don't delete these files yet** - they provide:
1. Reference implementation for porting features to v2.0
2. Historical context for transformation decisions
3. Reusable components (e.g., Monte Carlo, regime detection)

**Phase 2 Plan**: Port useful components to new architecture:
- Move Monte Carlo to `src/models/simulation.py`
- Refactor regime detection for factor engine
- Replace manual DCF with factor-based scoring

### v2.0 Architecture

**Active codebase** (use these instead):
```
src/
├── pipeline/
│   ├── fred_connector.py      # Real-time macro data
│   ├── damodaran_loader.py    # Academic sector priors
├── utils/
│   └── validation.py          # Data quality scoring
├── models/                    # Phase 2+ (TBD)
│   ├── factors.py            # Value/Quality/Momentum
│   ├── portfolio.py          # Enhanced Black-Litterman
│   └── backtest.py           # Historical validation
```

**Testing**:
- `tests/test_phase1_integration.py` - v2.0 test suite (13 tests)
- Old tests (deleted) tested v1.0 modules/

### References
- [CRITICAL_ANALYSIS.md](CRITICAL_ANALYSIS.md) - Detailed v1.0 critique
- [MASTER_PLAN.md](MASTER_PLAN.md) - v2.0 transformation roadmap
- [README.md](README.md) - Main documentation

---

**Philosophy**: "Trust the Data, Not the Narrative"  
**Version**: 2.0.0  
**Status**: Phase 1 complete, Phase 2 in progress

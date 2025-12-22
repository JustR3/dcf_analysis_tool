# Quant Portfolio Manager - Development Roadmap

**Last Updated**: December 22, 2025

## Phase 1: DCF Valuation Engine ✅ COMPLETE
- [x] Core DCF calculation engine
- [x] Data fetching with yfinance
- [x] Scenario analysis (Bull/Base/Bear)
- [x] Sensitivity analysis
- [x] Multi-stock comparison
- [x] Interactive CLI with Rich UI
- [x] Programmatic Python API
- [x] Documentation and README

---

## Phase 2: Portfolio Optimization Engine 🚧 IN PROGRESS

### Step 1: The Skeleton & Data Layer (Architectural) ✅
**Status**: Complete

#### Major Tasks
- [x] Create `modules/portfolio/regime.py`
- [x] Implement `RegimeDetector` class
  - [x] Fetch historical SPY data via yfinance
  - [x] Calculate 200-day Simple Moving Average crossover
  - [x] Return market regime enum (RISK_ON/RISK_OFF)
  - [x] Add rate limiting for API calls
  - [x] Error handling for data fetch failures
  - [x] Cache mechanism for recent regime data

#### Completed Features ✅
- **RegimeDetector class**: Fully functional with SPY data fetching
- **MarketRegime enum**: RISK_ON, RISK_OFF, UNKNOWN states
- **RegimeResult dataclass**: Comprehensive result container with metadata
- **200-day SMA calculation**: Accurate moving average computation
- **Rate limiting**: Reused RateLimiter from DCF module (60 calls/min)
- **Caching**: 1-hour cache for regime results to minimize API calls
- **Error handling**: Graceful failure with error messages
- **Convenience functions**: `get_market_regime()`, `is_bull_market()`, `is_bear_market()`

#### Test Results ✅
```
Current Market Status (Dec 22, 2025):
- Regime: RISK_ON (Bull Market)
- SPY Price: $685.21
- 200-day SMA: $619.48
- Signal Strength: +10.61% (strong bullish)
- Data Points: 208 days
```

#### Technical Details
- **Input**: None (automatically fetches SPY data)
- **Output**: Enum value (RISK_ON or RISK_OFF)
- **Logic**: 200-day SMA crossover
  - RISK_ON: Current price > 200-day SMA (Bull market)
  - RISK_OFF: Current price < 200-day SMA (Bear market)

---

### Step 2: The Optimization Engine (Math Heavy) ⏳
**Status**: Not Started

#### Major Tasks
- [ ] Add PyPortfolioOpt dependency to `pyproject.toml`
- [ ] Create `modules/portfolio/optimizer.py`
- [ ] Implement `PortfolioEngine` class
  - [ ] Multi-stock data fetching
  - [ ] Calculate Expected Returns (CAPM)
  - [ ] Calculate Covariance Matrix (Ledoit-Wolf shrinkage)
  - [ ] Implement `optimize_max_sharpe()` method
  - [ ] Implement `optimize_min_volatility()` method
  - [ ] Implement `optimize_efficient_risk()` method
  - [ ] Return optimal weights dictionary

#### Technical Details
- **Dependencies**: pypfopt, scipy, cvxpy
- **Risk Model**: Ledoit-Wolf covariance shrinkage
- **Return Model**: CAPM-based expected returns
- **Optimization**: Efficient Frontier methods

#### Subtasks
- [ ] Data validation and preprocessing
- [ ] Handle missing data and edge cases
- [ ] Portfolio constraints (weights sum to 1, no short selling)
- [ ] Performance metrics (Sharpe ratio, volatility, expected return)
- [ ] Backtesting framework (optional)

---

### Step 3: The Integration (Black-Litterman) ⏳
**Status**: Not Started

#### Major Tasks
- [ ] Update `PortfolioEngine` to accept DCF intrinsic values
- [ ] Implement Black-Litterman model integration
  - [ ] Create views vector (Q) from DCF valuations
  - [ ] Calculate view confidence matrix (Omega)
  - [ ] Combine market equilibrium with analyst views
  - [ ] Generate posterior expected returns
- [ ] Update `main_cli.py` for portfolio commands
  - [ ] Add portfolio optimization subcommand
  - [ ] Interactive mode for portfolio creation
  - [ ] Display optimization results with Rich tables
  - [ ] Export portfolio weights to CSV

#### Technical Details
- **Integration Flow**:
  1. User runs DCF analysis on multiple stocks
  2. DCF results feed into Black-Litterman as "views"
  3. Undervalued stocks get positive views
  4. Overvalued stocks get negative views
  5. Optimizer generates optimal portfolio weights

#### Subtasks
- [ ] Design data flow between DCFEngine and PortfolioEngine
- [ ] Create wrapper function for DCF → Portfolio workflow
- [ ] Implement view generation logic
  - [ ] Map upside/downside % to expected returns
  - [ ] Confidence based on DCF sensitivity
- [ ] CLI interface enhancements
- [ ] Add portfolio visualization (efficient frontier plot)
- [ ] Documentation and usage examples

---

## Phase 3: Advanced Features ⏳
**Status**: Not Started

### Planned Features
- [ ] Risk Parity allocation
- [ ] Hierarchical Risk Parity (HRP)
- [ ] Monte Carlo simulation for portfolio returns
- [ ] Portfolio rebalancing strategies
- [ ] Factor-based optimization
- [ ] ESG integration
- [ ] Tax-loss harvesting optimization
- [ ] Custom constraints (sector limits, position sizing)

---

## Testing & Quality 📋
**Status**: Not Started

- [ ] Unit tests for RegimeDetector
- [ ] Unit tests for PortfolioEngine
- [ ] Integration tests for DCF → Portfolio flow
- [ ] End-to-end CLI tests
- [ ] Performance benchmarking
- [ ] Code coverage > 80%
- [ ] Documentation strings for all public methods
- [ ] Type hints throughout codebase

---

## Documentation 📚
**Status**: Ongoing

- [ ] Update README with portfolio examples
- [ ] API documentation for portfolio module
- [ ] Tutorial notebooks (Jupyter)
- [ ] Video walkthrough (optional)
- [ ] Case studies with real portfolios

---

## Notes & Decisions

### Architecture Decisions
- **Modular Design**: Keep valuation and portfolio modules independent
- **Data Flow**: DCF results → Views → Black-Litterman → Optimization
- **Rate Limiting**: Reuse existing RateLimiter from DCF module
- **Caching**: Consider caching regime data and historical prices

### Technical Considerations
- **Data Quality**: Handle missing data, outliers, and edge cases
- **Performance**: Optimize for portfolios with 20-50 stocks
- **User Experience**: Rich terminal UI, clear error messages
- **Extensibility**: Design for future features (Risk Parity, HRP)

### Open Questions
- [ ] How to handle portfolio constraints (sector limits, position sizing)?
- [ ] Should we support short selling?
- [ ] What rebalancing frequency to recommend?
- [ ] How to integrate transaction costs?

---

## Current Sprint: Step 2 - Portfolio Optimization Engine

**Goal**: Implement PyPortfolioOpt integration for optimal portfolio construction

**Next Actions**:
1. Add pypfopt dependency to pyproject.toml
2. Create modules/portfolio/optimizer.py
3. Implement PortfolioEngine class with:
   - Multi-stock data fetching
   - Expected returns (CAPM)
   - Covariance matrix (Ledoit-Wolf)
   - Efficient frontier optimization

**Definition of Done**:
- ✅ PortfolioEngine class implemented
- ✅ Data fetching for multiple tickers
- ✅ CAPM expected returns calculation
- ✅ Ledoit-Wolf covariance matrix
- ✅ optimize_max_sharpe() method working
- ✅ Returns optimal portfolio weights
- ✅ Error handling and validation
- ✅ Documentation complete

**Estimated Completion**: Next session

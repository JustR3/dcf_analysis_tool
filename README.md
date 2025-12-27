# Quant Portfolio Manager

> **Systematic quantitative finance platform for data-driven portfolio construction.**

A production-ready system combining real-time macroeconomic data, academic financial research, and multi-factor stock ranking with transparent verification mechanisms.

## 🎯 Overview

The Quant Portfolio Manager implements a systematic approach to quantitative investing through three integrated phases:

1. **Data Foundation**: Real-time FRED economic indicators and Damodaran academic datasets
2. **Factor Engine**: Multi-factor stock ranking using Value, Quality, and Momentum signals
3. **Portfolio Optimization**: Black-Litterman portfolio construction with DCF integration

## ✨ Key Features

### 📊 Real-Time Data Integration
- **FRED Connector**: Live risk-free rate, inflation, and macroeconomic indicators from Federal Reserve Economic Data
- **Damodaran Loader**: Academic datasets from NYU Stern (sector betas, equity risk premiums, industry margins)
- **Data Validation**: Cross-verification and quality checks before processing

### 🔬 Factor-Based Stock Ranking
- **Value Factor**: FCF Yield (50%) + Earnings Yield (50%)
- **Quality Factor**: ROIC (50%) + Gross Margin (50%)
- **Momentum Factor**: 12-month price return
- **Z-Score Normalization**: Statistical standardization with winsorization (±3σ)
- **Composite Scoring**: Weighted combination (40% Value, 40% Quality, 20% Momentum)

### 🔍 Glass Box Verification
- **Audit Reports**: Detailed factor breakdowns showing why each stock ranks high/low
- **Universe Comparison**: Individual stock metrics vs. universe statistics (mean, std, percentile)
- **Factor Contributions**: Transparent scoring showing each factor's impact on final rank
- **CLI Verification**: Interactive command-line tool for on-demand stock audits

### 🎯 Portfolio Construction
- **Factor-Based Black-Litterman**: Systematic portfolio optimization using factor scores as views
- **Confidence Weighting**: View certainty based on factor agreement (low std = high confidence)
- **View Generation**: Z-scores converted to implied excess returns
- **Discrete Allocation**: Integer share quantities with leftover tracking
- **Multiple Objectives**: Max Sharpe, Min Volatility, Max Quadratic Utility

### 💼 Legacy DCF System
- **DCF Valuation**: Fundamental analysis with Monte Carlo simulation
- **Risk Metrics**: VaR, CVaR, Sortino Ratio, Calmar Ratio, Max Drawdown
- **Market Regime Detection**: Adaptive allocation based on market conditions

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/justr3/quant-portfolio-manager.git
cd quant-portfolio-manager
uv sync
```

### Usage Examples

```bash
# Example 1: Verify a stock's factor ranking (Phase 2)
python main.py verify NVDA

# Example 2: Compare a stock against custom universe
python main.py verify TSLA --universe NVDA XOM JPM PFE TSLA

# Example 3: Run full pipeline (Factor Engine → Portfolio Optimizer)
python test_full_pipeline.py
```

## 📖 Factor Methodology

### Value Factor
Measures how cheap a stock is relative to its cash generation:
- **FCF Yield**: Free Cash Flow / Market Cap (rewards cash generation)
- **Earnings Yield**: EBIT / Market Cap (operational profitability)
- **Interpretation**: Higher values indicate better valuation (cheaper stocks)

### Quality Factor
Measures fundamental business strength and profitability:
- **ROIC**: EBIT / Invested Capital (capital efficiency)
- **Gross Margin**: Gross Profit / Revenue (pricing power)
- **Interpretation**: Higher values indicate better quality (stronger businesses)

### Momentum Factor
Measures price trend strength:
- **12-Month Return**: (Price_Now / Price_12M_Ago) - 1
- **Interpretation**: Positive momentum indicates uptrend, negative indicates downtrend

### Z-Score Normalization
All factors are standardized using Z-scores for fair comparison:
- **Formula**: Z = (Value - Mean) / StdDev
- **Winsorization**: Capped at ±3 standard deviations to prevent outliers
- **Missing Data**: Stocks with insufficient data receive neutral score (0)

### Composite Score
Final ranking combines all three factors:
- **Total Score** = 0.4 × Value_Z + 0.4 × Quality_Z + 0.2 × Momentum_Z
- **Rationale**: Equal weight on fundamentals (Value + Quality), lower weight on price action (Momentum)

## 🎯 Portfolio Optimization

The Black-Litterman optimizer converts factor scores into systematic portfolio allocation:

### View Generation
Factor Z-scores are translated into expected excess returns:
- **Formula**: `Implied_Return = Z_Score × Volatility × Alpha_Scalar`
- **Alpha Scalar**: Configurable parameter (default 0.02 = 2% per sigma beat)
- **Example**: Stock with Total_Score = 1.0, Volatility = 25% → View = +0.50% excess return

### Confidence Calculation
Confidence is based on factor agreement (standard deviation of Z-scores):
- **High Confidence (0.8)**: Std Dev < 0.5 (all factors agree)
- **Medium Confidence (0.4-0.6)**: Std Dev 0.5-1.5 (mixed signals)
- **Low Confidence (0.2)**: Std Dev > 1.5 (factors disagree)

### Optimization Process
1. **Prior Returns**: Historical mean returns as market equilibrium
2. **Views Matrix**: Factor-implied excess returns for each stock
3. **Omega Matrix**: Idzorek method scales uncertainty by confidence
4. **Posterior Returns**: Bayesian update combining prior + views
5. **Optimization**: Max Sharpe / Min Volatility / Max Quadratic Utility

## 🔍 Verification System

The Glass Box verification layer provides full transparency into stock rankings:

### Audit Report Components
- **Rank & Percentile**: Stock's position within the universe
- **Factor Z-Scores**: Standardized scores for Value, Quality, Momentum
- **Raw Metrics**: Actual underlying values (ROIC, FCF Yield, 12M Return)
- **Universe Context**: How stock compares to mean/std of universe
- **Factor Contributions**: Each factor's impact on total score
- **Interpretation**: Plain-language explanation (Strong/Weak/Neutral)

### Example Output
```
🔍 FACTOR AUDIT REPORT: NVDA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 OVERALL RANKING
   Rank: #1 of 10 stocks
   Percentile: 100.0%
   Total Score: 0.591

📈 FACTOR BREAKDOWN
   VALUE:
      Z-Score: -0.75 (Weak/Negative)
      Raw Value: 0.0156 (Universe Mean: 0.0347)
      Contribution: -0.300
   
   QUALITY:
      Z-Score: 1.79 (Very Strong Positive)
      Raw Value: 0.8253 (Universe Mean: 0.3926)
      Contribution: +0.714
   
   MOMENTUM:
      Z-Score: 0.88 (Strong Positive)
      Raw Value: 0.3592 (Universe Mean: 0.1833)
      Contribution: +0.176

💡 SUMMARY
   Mixed profile. Strong in Quality, Momentum. Weak in Value.
```

## 📁 Project Structure

```
quant-portfolio-manager/
├── main.py                          # CLI entry point with verify command
├── config.py                        # Configuration and API keys
├── pyproject.toml                   # Dependencies (uv package manager)
├── src/
│   ├── models/
│   │   ├── factor_engine.py         # Multi-factor stock ranking engine
│   │   └── optimizer.py             # Factor-based Black-Litterman optimizer
│   ├── pipeline/
│   │   ├── fred_connector.py        # FRED API integration
│   │   └── damodaran_loader.py      # NYU Stern data loader
│   └── utils/
│       └── validation.py            # Data quality checks
├── modules/                         # Legacy v1.0 system (DCF/Monte Carlo)
│   ├── valuation/
│   │   └── dcf.py                   # DCF valuation engine
│   ├── portfolio/
│   │   ├── optimizer.py             # Legacy optimizer
│   │   └── regime.py                # Market regime detection
│   └── utils.py                     # Caching and utilities
├── tests/
│   └── test_phase1_integration.py   # Integration tests
├── test_full_pipeline.py            # End-to-end pipeline test
└── data/
    └── cache/                       # Data cache (gitignored)
```

## 🛠️ Technical Details

### Core Technologies
- **Python 3.12+**: Modern type hints, dataclasses
- **yfinance**: Yahoo Finance API for market data
- **pandas/numpy**: Data manipulation and statistical analysis
- **PyPortfolioOpt**: Black-Litterman optimization (Legacy)
- **Rich**: Terminal UI with formatted tables

### Data Pipeline
1. **FRED Connector**: Fetches real-time 10-year Treasury rate, inflation data
2. **Damodaran Loader**: Parses CSV files from NYU Stern (sector betas, ERP)
3. **Factor Engine**: Bulk downloads financial statements via yfinance
4. **Z-Score Calculation**: Statistical normalization across universe
5. **View Generation**: Converts Z-scores to Black-Litterman views
6. **Portfolio Optimization**: Bayesian allocation with confidence weighting
7. **Discrete Allocation**: Integer share quantities with leftover tracking

### Key Algorithms
- **Z-Score Normalization**: `Z = (X - μ) / σ` with ±3σ winsorization
- **Composite Scoring**: Weighted sum of standardized factors
- **View Generation**: `Implied_Return = Z_Score × Volatility × Alpha_Scalar`
- **Confidence Scoring**: Based on factor agreement (std dev of Z-scores)
- **Black-Litterman**: Bayesian posterior = (Prior + Views weighted by confidence)
- **Missing Data Handling**: NaN → 0 (neutral score), dropna for statistics
- **Bulk Data Fetching**: Single yfinance call for entire universe (performance optimization)

### Factor Calculation Details

**Value Factor:**
```
FCF Yield = Free Cash Flow / Market Cap
Earnings Yield = EBIT / Market Cap
Value Score = 0.5 × FCF_Yield + 0.5 × Earnings_Yield
```

**Quality Factor:**
```
ROIC = EBIT / (Total Assets - Current Liabilities)
Gross Margin = Gross Profit / Revenue
Quality Score = 0.5 × ROIC + 0.5 × Gross_Margin
```

**Momentum Factor:**
```
Momentum = (Price_Current / Price_252_Days_Ago) - 1
```

**Black-Litterman View Generation:**
```
Implied_Return = Total_Z_Score × Annualized_Volatility × Alpha_Scalar
Confidence = f(std_dev(Value_Z, Quality_Z, Momentum_Z))
  where f(x) = 0.8 if x < 0.5, 0.6 if x < 1.0, 0.4 if x < 1.5, else 0.2
```

## 📊 Implementation Status

### ✅ Phase 1: Data Foundation (Complete)
- FRED real-time economic data integration
- Damodaran academic dataset parsing
- Data validation framework

### ✅ Phase 2: Factor Engine (Complete)
- Multi-factor stock ranking (Value, Quality, Momentum)
- Z-score normalization with winsorization
- Glass box verification system with audit reports
- CLI interface for interactive verification

### ✅ Phase 3: Portfolio Optimizer (Complete)
- Factor-based Black-Litterman optimization
- View generation from factor Z-scores
- Confidence weighting based on factor agreement
- Max Sharpe / Min Volatility / Max Quadratic Utility objectives
- Discrete allocation with integer shares
- Full pipeline integration (Factor Engine → Optimizer)

### 💼 Legacy Systems (Operational)
- DCF valuation with Monte Carlo simulation
- Market regime detection
- Comprehensive risk metrics (VaR, CVaR, Sortino, Calmar)

## 📚 Academic Foundation

### Factor Investing
- **Value Premium**: Fama & French (1992) - Value stocks outperform growth
- **Quality Factor**: Piotroski F-Score (2000) - Fundamental strength predicts returns
- **Momentum Effect**: Jegadeesh & Titman (1993) - Past winners continue winning

### Risk Premia
- **Damodaran Data**: Industry cost of capital, sector betas, equity risk premiums
- **FRED Integration**: Real-time risk-free rate (10Y Treasury) for CAPM

### Portfolio Theory
- **Black-Litterman**: Black & Litterman (1992) - Bayesian portfolio optimization
- **Factor-Based Views**: Factor scores as return expectations

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

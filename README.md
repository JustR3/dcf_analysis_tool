# Quant Portfolio Manager

> **A production-ready quantitative finance toolkit combining fundamental analysis with modern portfolio theory.**

Quant Portfolio Manager seamlessly integrates DCF (Discounted Cash Flow) valuation with Black-Litterman portfolio optimization, enabling data-driven investment decisions backed by fundamental analysis and market equilibrium theory.

## ✨ Key Features

### 📊 DCF Valuation Engine
Professional-grade discounted cash flow analysis with real-time market data:
- **Automated Fair Value Calculation** - WACC, growth rates, and terminal value
- **Scenario Analysis** - Bull/Base/Bear cases for risk assessment  
- **Sensitivity Tables** - Test robustness of assumptions
- **Multi-Stock Comparison** - Rank opportunities by upside potential
- **Export Capabilities** - CSV output for further analysis

### 🎯 Portfolio Optimization
Black-Litterman model with DCF integration for optimal asset allocation:
- **DCF-Driven Views** - Fundamental valuations inform expected returns
- **Market Regime Detection** - 200-day SMA + VIX term structure analysis
- **Multiple Strategies** - Max Sharpe, Min Volatility, Efficient Risk
- **Discrete Allocation** - Integer shares with leftover cash tracking
- **Confidence Weighting** - Blend fundamental views with market equilibrium

### 🎨 Modern Interface
Built for both interactive use and programmatic integration:
- **Rich Terminal UI** - Beautiful, colorful output with tables and panels
- **Interactive Prompts** - Guided workflows for complex analyses
- **Python API** - Full programmatic access for automation
- **CLI Commands** - Quick one-liners for power users

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/justr3/quant-portfolio-manager.git
cd quant-portfolio-manager

# Install dependencies with uv (recommended)
uv sync

# Or with pip
pip install -r requirements.txt
```

### 5-Minute Demo

```bash
# 1. Interactive mode - guided prompts walk you through
uv run main.py

# 2. Quick DCF valuation
uv run main.py valuation AAPL

# 3. Build an optimized portfolio
uv run main.py portfolio
```

## 📖 Documentation

### Table of Contents
- [DCF Valuation](#dcf-valuation)
  - [Command-Line Interface](#dcf-cli-usage)
  - [Python API](#dcf-python-api)
- [Portfolio Optimization](#portfolio-optimization)
  - [Command-Line Interface](#portfolio-cli-usage)
  - [Python API](#portfolio-python-api)
- [Market Regime Detection](#market-regime-detection)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)

---

## 💰 DCF Valuation

### DCF CLI Usage

```bash
# Basic valuation
uv run main.py valuation AAPL

# Custom parameters
uv run main.py valuation TSLA --growth 12 --wacc 10 --years 5

# Scenario analysis (Bull/Base/Bear)
uv run main.py valuation MSFT --scenarios

# Sensitivity analysis
uv run main.py valuation GOOGL --sensitivity

# Compare multiple stocks
uv run main.py valuation AAPL MSFT GOOGL NVDA --compare --export results.csv
```

### DCF Python API

**Basic Usage:**

**Basic Usage:**

```python
from modules.valuation import DCFEngine

# Quick valuation
engine = DCFEngine("AAPL", auto_fetch=True)
result = engine.get_intrinsic_value()

print(f"Fair Value: ${result['value_per_share']:.2f}")
print(f"Current Price: ${result['current_price']:.2f}")
print(f"Upside: {result['upside_downside']:+.1f}%")
print(f"Assessment: {result['assessment']}")
```

**Custom Parameters:**
result = engine.get_intrinsic_value(
    growth=0.10,        # 10% revenue growth
    wacc=0.12,          # 12% discount rate
    term_growth=0.025,  # 2.5% terminal growth
    years=5             # 5-year forecast horizon
)

**Custom Parameters:**

```python
# Customize DCF assumptions
result = engine.get_intrinsic_value(
    growth=0.10,        # 10% revenue growth
    wacc=0.12,          # 12% discount rate
    term_growth=0.025,  # 2.5% terminal growth
    years=5             # 5-year forecast horizon
)
```

**Scenario & Sensitivity Analysis:**

```python
# Scenario analysis (Bull/Base/Bear)
scenarios = engine.run_scenario_analysis()
for scenario in ["Bull", "Base", "Bear"]:
    data = scenarios[scenario]
    print(f"{scenario}: ${data['value_per_share']:.2f} ({data['upside_downside']:+.1f}%)")

# Sensitivity analysis
sensitivity = engine.run_sensitivity_analysis()
```

**Multi-Stock Comparison:**

```python
# Compare multiple stocks
comparison = DCFEngine.compare_stocks(["AAPL", "MSFT", "GOOGL", "NVDA"])

print("Ranked by Upside Potential:")
for rank, ticker in enumerate(comparison["ranking"], 1):
    data = comparison["results"][ticker]
    print(f"{rank}. {ticker}: {data['upside_downside']:+.1f}%")
```

---

## 📈 Portfolio Optimization

Integrate fundamental analysis with modern portfolio theory using Black-Litterman model.

### Portfolio CLI Usage

```bash
# Interactive workflow
uv run main.py portfolio

# The system will:
# 1. Prompt for stock tickers
# 2. Run DCF analysis on each
# 3. Detect market regime (RISK_ON/RISK_OFF)
# 4. Optimize using Black-Litterman with DCF views
# 5. Display optimal weights and discrete allocation
```

### Portfolio Python API

**End-to-End Workflow:**

```python
from modules.valuation import DCFEngine
from modules.portfolio import optimize_portfolio_with_dcf, OptimizationMethod

# Step 1: Run DCF analysis
tickers = ['AAPL', 'MSFT', 'GOOGL', 'NVDA']
dcf_results = {}

for ticker in tickers:
    engine = DCFEngine(ticker, auto_fetch=True)
    if engine.is_ready:
        dcf_results[ticker] = engine.get_intrinsic_value()

# Step 2: Optimize portfolio with Black-Litterman
portfolio = optimize_portfolio_with_dcf(
    dcf_results=dcf_results,
    method=OptimizationMethod.MAX_SHARPE,
    period="2y",
    confidence=0.3,  # 30% weight to DCF views
)

print(f"Expected Return: {portfolio.expected_annual_return:.2f}%")
print(f"Volatility: {portfolio.annual_volatility:.2f}%")
print(f"Sharpe Ratio: {portfolio.sharpe_ratio:.2f}")
print(f"Weights: {portfolio.weights}")
```

**Advanced Control:**

**Advanced Control:**

```python
from modules.portfolio import PortfolioEngine, OptimizationMethod

# Manual workflow for maximum flexibility
engine = PortfolioEngine(tickers=['AAPL', 'MSFT', 'GOOGL', 'NVDA'])
engine.fetch_data(period='2y')

# Optimize with DCF views
result = engine.optimize_with_views(
    dcf_results=dcf_results,
    confidence=0.4,  # Higher confidence = more weight to DCF
    method=OptimizationMethod.MAX_SHARPE
)

# Get discrete allocation for $50,000 portfolio
allocation = engine.get_discrete_allocation(total_portfolio_value=50000)
print(f"Shares: {allocation.allocation}")
print(f"Leftover: ${allocation.leftover:.2f}")
```

---

## 🌡️ Market Regime Detection

Automatically detect market conditions using technical and volatility indicators:

```python
from modules.portfolio import RegimeDetector

detector = RegimeDetector()

# Combined regime (SPY SMA + VIX term structure)
regime = detector.get_current_regime(method="combined")
print(f"Market Regime: {regime}")  # RISK_ON, RISK_OFF, or CAUTION

# Get detailed regime information
result = detector.get_regime_with_details()
print(f"SPY Price: ${result.current_price:.2f}")
print(f"200-day SMA: ${result.sma_200:.2f}")
print(f"VIX Structure: {result.vix_structure.to_dict()}")
```

**Regime Signals:**
- **RISK_ON**: SPY above 200-day SMA + VIX in contango (normal conditions)
- **RISK_OFF**: SPY below 200-day SMA + VIX in backwardation (panic)
- **CAUTION**: Mixed signals or elevated volatility

---

## 📦 Project Structure

```
quant-portfolio-manager/
├── main.py                      # CLI entry point
├── modules/
│   ├── __init__.py
│   ├── valuation/
│   │   ├── __init__.py
│   │   └── dcf.py              # DCF valuation engine
│   └── portfolio/
│       ├── __init__.py
│       ├── optimizer.py        # Portfolio optimization
│       └── regime.py           # Market regime detection
├── pyproject.toml              # Project configuration
├── uv.lock                     # Dependency lock
├── README.md
├── TODO.md
└── LICENSE
```

---

## 🛠️ Technical Stack

**Core Technologies:**
- **Python 3.12+** - Modern Python with type hints
- **yfinance** - Real-time market data
- **PyPortfolioOpt** - Portfolio optimization algorithms
- **NumPy & Pandas** - Numerical computing
- **Rich** - Terminal UI
- **Questionary** - Interactive prompts

**Algorithms:**
- **DCF Valuation** - Explicit forecast + Gordon Growth terminal value
- **Black-Litterman** - Bayesian posterior with analyst views
- **Mean-Variance** - Markowitz efficient frontier
- **Regime Detection** - 200-day SMA + VIX term structure

---

## 📊 Dependencies

## 📊 Dependencies

**Production:**
```toml
yfinance >= 0.2.32        # Market data
pandas >= 2.0.0           # Data manipulation
rich >= 13.0.0            # Terminal UI
questionary >= 2.0.0      # Interactive prompts
pyportfolioopt >= 1.5.5   # Optimization algorithms
scipy >= 1.11.0           # Scientific computing
cvxpy >= 1.4.0            # Convex optimization
scikit-learn >= 1.3.0     # Machine learning utilities
```

**Development:**
```toml
pytest >= 7.0.0           # Testing
pytest-cov >= 4.0.0       # Coverage
ruff >= 0.1.0             # Linting & formatting
```

---

## 🎯 Use Cases

**1. Value Investing Screen**
```bash
# Find undervalued stocks
uv run main.py valuation AAPL MSFT GOOGL AMZN META --compare -e undervalued.csv
```

**2. Portfolio Construction**
```python
# Build DCF-driven portfolio
dcf_results = {...}  # Your DCF analysis
portfolio = optimize_portfolio_with_dcf(dcf_results, confidence=0.3)
```

**3. Risk Assessment**
```bash
# Test valuation sensitivity
uv run main.py valuation TSLA --sensitivity
```

**4. Market Timing**
```python
# Check regime before deploying capital
regime = RegimeDetector().get_current_regime()
if regime == MarketRegime.RISK_ON:
    # Deploy aggressive strategy
```

---

## 🧪 Testing

```bash
# Run test suite
uv run pytest

# With coverage report
uv run pytest --cov=modules --cov-report=html

# Lint code
uv run ruff check .
```

---

## 🗺️ Roadmap

### ✅ Completed (v0.1.0)
- [x] DCF valuation engine with scenario/sensitivity analysis
- [x] Black-Litterman portfolio optimization
- [x] Market regime detection (SPY SMA + VIX)
- [x] Interactive CLI with Rich UI
- [x] Python API for programmatic access
- [x] Discrete share allocation

### 🔜 Coming Soon (v0.2.0)
- [ ] Risk Parity allocation
- [ ] Hierarchical Risk Parity (HRP)
- [ ] Monte Carlo simulation
- [ ] Factor models (Fama-French)
- [ ] Backtesting framework
- [ ] Tax-loss harvesting

### 💡 Future Ideas
- [ ] Options pricing (Black-Scholes)
- [ ] ESG integration
- [ ] Real-time portfolio tracking
- [ ] Web dashboard
- [ ] API service

---

## 🤝 Contributing

Contributions welcome! Areas of interest:
- **Testing**: Unit tests for core modules
- **Documentation**: Tutorials and examples
- **Features**: New optimization methods or analysis tools
- **Performance**: Optimization and caching improvements

**Process:**
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built with excellent open-source tools:
- [yfinance](https://github.com/ranaroussi/yfinance) - Yahoo Finance API
- [PyPortfolioOpt](https://github.com/robertmartin8/PyPortfolioOpt) - Portfolio optimization
- [Rich](https://github.com/Textualize/rich) - Terminal formatting
- [Questionary](https://github.com/tmbo/questionary) - Interactive prompts

---

## ⚠️ Disclaimer

**For educational and research purposes only.**

This tool is not financial advice. Always:
- Conduct your own research
- Consult licensed financial professionals
- Understand the risks before investing
- Verify all calculations independently

Past performance does not guarantee future results.

---

<div align="center">

**[Documentation](#documentation)** • **[Examples](#dcf-valuation)** • **[Issues](https://github.com/justr3/quant-portfolio-manager/issues)** • **[Discussions](https://github.com/justr3/quant-portfolio-manager/discussions)**

Made with ❤️ for quantitative finance

</div>

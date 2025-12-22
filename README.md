# Quant Portfolio Manager

A modular Python toolkit for quantitative finance analysis, featuring a professional DCF (Discounted Cash Flow) valuation engine with interactive CLI and programmatic API.

## 🎯 Features

### ✅ DCF Valuation Engine (Active)
- **Real-time financial data** fetching via yfinance
- **Standard DCF analysis** with customizable parameters
- **Scenario analysis** (Bull/Base/Bear cases)
- **Sensitivity analysis** for key assumptions
- **Multi-stock comparison** with ranking
- **Interactive CLI** with rich terminal UI
- **Programmatic API** for integration

### 🔜 Portfolio Optimization (Coming Soon)
- Mean-Variance Optimization (Markowitz)
- Risk Parity
- Black-Litterman Model
- Fundamental-weighted portfolios using DCF data

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/quant-portfolio-manager.git
cd quant-portfolio-manager

# Install dependencies (requires uv)
uv sync
```

### Command-Line Usage

```bash
# Interactive mode (guided prompts)
uv run main_cli.py

# Quick analysis of a single stock
uv run main_cli.py valuation AAPL

# Custom parameters
uv run main_cli.py valuation AAPL --growth 8 --wacc 11 --years 5

# Scenario analysis (Bull/Base/Bear)
uv run main_cli.py valuation MSFT --scenarios

# Sensitivity analysis
uv run main_cli.py valuation GOOGL --sensitivity

# Compare multiple stocks
uv run main_cli.py valuation AAPL MSFT GOOGL NVDA --compare

# Export comparison results to CSV
uv run main_cli.py valuation AAPL MSFT GOOGL --compare --export results.csv
```

## 📦 Project Structure

```
quant-portfolio-manager/
├── main_cli.py              # CLI entry point
├── modules/
│   ├── __init__.py
│   ├── valuation/           # DCF Valuation Engine
│   │   ├── __init__.py
│   │   └── dcf.py           # DCFEngine class
│   └── portfolio/           # Portfolio Optimization (coming soon)
│       └── __init__.py
├── pyproject.toml           # Project configuration & dependencies
├── uv.lock                  # Dependency lock file
├── README.md
└── LICENSE
```

## 💻 Usage Examples

### DCF Valuation Engine

The DCF module provides both a command-line interface and a Python API.

#### CLI Usage

```bash
# Basic valuation with automatic parameter detection
uv run main_cli.py valuation AAPL

# Customize growth assumptions
uv run main_cli.py valuation TSLA --growth 12 --wacc 10

# Scenario analysis for investment thesis validation
uv run main_cli.py valuation MSFT --scenarios

# Sensitivity analysis to test assumption robustness
uv run main_cli.py valuation GOOGL --sensitivity

# Compare multiple stocks to find best value
uv run main_cli.py valuation AAPL MSFT GOOGL NVDA --compare --export comparison.csv
```

#### Python API

The refactored engine provides a clean, importable API for integration:

```python
from modules.valuation import DCFEngine

# Initialize engine (auto-fetches data)
engine = DCFEngine("AAPL")

# Get intrinsic value with default parameters
result = engine.get_intrinsic_value()
print(f"Fair Value: ${result['value_per_share']:.2f}")
print(f"Current Price: ${result['current_price']:.2f}")
print(f"Upside: {result['upside_downside']:+.1f}%")
print(f"Assessment: {result['assessment']}")

# Customize DCF assumptions
result = engine.get_intrinsic_value(
    growth=0.10,        # 10% revenue growth
    wacc=0.12,          # 12% discount rate
    term_growth=0.025,  # 2.5% terminal growth
    years=5             # 5-year forecast horizon
)

# Run scenario analysis (Bull/Base/Bear)
scenarios = engine.run_scenario_analysis()
for scenario in ["Bull", "Base", "Bear"]:
    data = scenarios[scenario]
    print(f"{scenario}: ${data['value_per_share']:.2f} ({data['upside_downside']:+.1f}%)")

# Sensitivity analysis
sensitivity = engine.run_sensitivity_analysis()
print("Growth Rate Sensitivity:")
for growth_rate, fair_value in sensitivity["growth_sensitivity"].items():
    print(f"  {growth_rate:.1f}%: ${fair_value:.2f}")

# Multi-stock comparison
comparison = DCFEngine.compare_stocks(["AAPL", "MSFT", "GOOGL", "NVDA"])
print(f"\nRanked by Upside Potential:")
for rank, ticker in enumerate(comparison["ranking"], 1):
    data = comparison["results"][ticker]
    print(f"{rank}. {ticker}: {data['upside_downside']:+.1f}%")

# Export to DataFrame for further analysis
import pandas as pd
df = engine.to_dataframe()
print(df)  # Year-by-year cash flow projections
```

#### Advanced Usage: Batch Analysis

```python
from modules.valuation import DCFEngine
import pandas as pd

# Analyze a portfolio of stocks
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
results = []

for ticker in tickers:
    engine = DCFEngine(ticker)
    if engine.is_ready:
        val = engine.get_intrinsic_value()
        results.append({
            "Ticker": ticker,
            "Current": val["current_price"],
            "Fair Value": val["value_per_share"],
            "Upside": val["upside_downside"],
            "Assessment": val["assessment"]
        })

df = pd.DataFrame(results)
print(df.sort_values("Upside", ascending=False))
```

## 🔧 Architecture Improvements

### Major Refactoring (v0.1.0)

The codebase has undergone a significant refactoring to improve modularity and maintainability:

#### Before (Monolithic `app.py`)
- Single 900+ line file with all functionality
- CLI-only interface with hard-coded outputs
- Difficult to import and reuse
- Tightly coupled data fetching and presentation

#### After (Modular Structure)
- **Separated concerns**: `DCFEngine` class for calculations, `main_cli.py` for interface
- **Clean API**: Importable engine with structured return types
- **Dataclasses**: Type-safe data containers (`CompanyData`, `DCFResult`, `ValuationResult`)
- **Flexible display**: Support for Rich terminal UI or plain text fallback
- **Programmatic access**: Full functionality available via Python API
- **Better testing**: Modular structure enables unit testing

#### Key Improvements
1. **`modules/valuation/dcf.py`**: Core DCF calculation engine (865 lines)
   - Data fetching with rate limiting
   - DCF calculations (explicit forecast + terminal value)
   - Scenario and sensitivity analysis
   - Multi-stock comparison

2. **`main_cli.py`**: User-facing CLI (979 lines)
   - Interactive menu system
   - Rich terminal formatting
   - Argument parsing for direct commands
   - CSV export functionality

3. **Dependencies**: Enhanced with professional tools
   - `rich`: Beautiful terminal output
   - `questionary`: Interactive prompts
   - `yfinance`: Real-time financial data
   - `pandas`: Data manipulation

## 📚 Portfolio Optimization Module *(Coming Soon)*

Planned features:
- **Mean-Variance Optimization** (Markowitz efficient frontier)
- **Risk Parity** allocation
- **Black-Litterman Model** for incorporating market views
- **Fundamental-weighted portfolios** using DCF intrinsic values
- Integration with DCF engine for valuation-driven allocation

## 📋 CLI Reference

```
usage: quant-portfolio-manager [-h] {valuation,val,dcf,portfolio,port,opt} ...

Quant Portfolio Manager - DCF Valuation & Portfolio Optimization

Commands:
  valuation (val, dcf)     DCF Valuation Engine
  portfolio (port, opt)    Portfolio Optimization (Coming Soon)

Valuation Options:
  tickers                  Stock ticker symbol(s)
  -g, --growth GROWTH      Forecast growth rate (%)
  -t, --terminal-growth    Terminal growth rate (%) [default: 2.5]
  -w, --wacc WACC          Discount rate / WACC (%)
  -y, --years YEARS        Forecast horizon [default: 5]
  -s, --scenarios          Run Bull/Base/Bear scenario analysis
  --sensitivity            Run sensitivity analysis
  -c, --compare            Compare multiple stocks
  -e, --export FILE        Export results to CSV
  -h, --help               Show help message

Examples:
  # Interactive mode with guided prompts
  uv run main_cli.py
  
  # Quick valuation
  uv run main_cli.py valuation AAPL
  
  # Custom parameters
  uv run main_cli.py valuation AAPL -g 8 -w 11 -y 5
  
  # Scenario analysis
  uv run main_cli.py valuation MSFT --scenarios
  
  # Multi-stock comparison with export
  uv run main_cli.py valuation AAPL MSFT GOOGL -c -e results.csv
```

## 🛠️ Requirements

- **Python**: 3.12+
- **Package Manager**: [uv](https://github.com/astral-sh/uv) (recommended) or pip

## 📦 Dependencies

### Core Dependencies
- **`yfinance`** (≥0.2.32): Real-time financial data from Yahoo Finance
- **`pandas`** (≥2.0.0): Data manipulation and analysis
- **`rich`** (≥13.0.0): Beautiful terminal output and formatting
- **`questionary`** (≥2.0.0): Interactive command-line prompts

### Development Dependencies
- **`pytest`** (≥7.0.0): Testing framework
- **`pytest-cov`** (≥4.0.0): Code coverage
- **`ruff`** (≥0.1.0): Fast Python linter and formatter

## 🧪 Testing

```bash
# Run tests (when test suite is added)
uv run pytest

# Run with coverage
uv run pytest --cov=modules
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- Financial data provided by [yfinance](https://github.com/ranaroussi/yfinance)
- Terminal UI powered by [Rich](https://github.com/Textualize/rich)
- Interactive prompts by [Questionary](https://github.com/tmbo/questionary)

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Note**: This tool is for educational and research purposes only. Always conduct your own research and consult with financial professionals before making investment decisions.

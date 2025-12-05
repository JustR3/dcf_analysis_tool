# DCF Analysis Tool

A terminal-based **Discounted Cash Flow (DCF)** valuation tool that fetches real financial data from Yahoo Finance and calculates fair share value for stocks.

## Overview

This tool automates the DCF valuation process by:
1. **Fetching real financial data** from yfinance (Free Cash Flow, shares outstanding, stock price, etc.)
2. **Gathering user assumptions** for growth rates and discount rates
3. **Projecting future cash flows** over an explicit forecast period
4. **Calculating terminal value** beyond the forecast horizon
5. **Comparing fair value** to current market price

## Setup

### Prerequisites
- Python 3.12 or higher
- Internet connection (for data fetching)

### Installation

1. **Clone or download** the project directory

2. **Install dependencies**:
   ```bash
   uv add yfinance pandas
   ```
   Or alternatively with pip:
   ```bash
   pip install yfinance>=0.2.32 pandas>=2.0.0
   ```

3. **Verify installation**:
   ```bash
   python -c "import yfinance; print('yfinance installed successfully')"
   ```

## Usage

### Basic Usage (Interactive Mode)

Run the tool with interactive prompts:
```bash
python app.py MSFT
```

### Coming Soon: Advanced Usage

Non-interactive mode with CLI arguments (v1.1.0):
```bash
# With custom parameters
python app.py MSFT --growth 8 --terminal-growth 2.5 --wacc 10 --years 5

# With scenario analysis
python app.py MSFT --scenarios

# Multi-stock comparison
python app.py AAPL MSFT GOOGL --compare

# Export results to CSV
python app.py MSFT --output results.csv
```

### Interactive Prompts

1. **Enter stock ticker** (e.g., "AAPL", "MSFT", "GOOGL")
   - The tool fetches real company financial data
   - Shows current price, market cap, and beta

2. **Explicit forecast growth rate** (default: 5%)
   - Expected annual FCF growth during forecast period
   - Typically 2-15% depending on industry and company maturity

3. **Terminal growth rate** (default: 2.5%)
   - Long-term growth rate after forecast period
   - Usually aligns with GDP growth (~2-3%)

4. **Discount rate / WACC** (default: auto-calculated)
   - Risk-adjusted return rate used to discount future cash flows
   - Auto-calculated as: Risk-free rate (4.5%) + Beta × Market risk premium (7%)
   - Can override with custom value

5. **Forecast horizon** (default: 5 years)
   - Number of years to explicitly project cash flows
   - Longer periods = more uncertainty but better captures long-term value

### Analyst Growth Estimates

The tool automatically fetches **analyst consensus growth estimates** from Yahoo Finance when available:
- Displays as: **"Analyst Est. Growth (1-5y)"** in the company info section
- Based on yfinance fields: `earningsGrowth` or `revenueGrowth`
- **User behavior:**
  - Press **Enter** without typing → Uses analyst estimate (if available) or default 5%
  - Enter custom value → Overrides analyst estimate
- **Not available?** The tool gracefully falls back to the 5% default
- Works for most major US stocks with analyst coverage

### Example Run

```
==================================================
DCF Analysis Tool - Real-World Financial Data
==================================================

Enter stock ticker (e.g., AAPL): MSFT
  Fetching data for MSFT...
✓ Data loaded for MSFT
  Current Price: $480.84
  Market Cap: $3574.16B
  Beta: 1.06
  Analyst Est. Growth (1-5y): 12.70%

=== DCF Model Parameters ===
Explicit forecast growth rate (%) [Default: 5.0 | Analyst: 12.70]: 
Terminal growth rate (%) [2.5]: 
Discount rate / WACC (%) [11.96]: 
Forecast horizon (years) [5]: 

==================================================
DCF VALUATION ANALYSIS - MSFT
==================================================

Year-by-Year Cash Flow Projections:
--------------------------------------------------
Year   FCF ($M)            PV ($M)
--------------------------------------------------
1          115,689         103,335
2          130,381         104,023
3          146,940         104,715
4          165,601         105,412
5          186,632         106,113
--------------------------------------------------
Sum PV (Explicit):             $        523,598M
Terminal PV:                   $      1,150,355M
--------------------------------------------------

VALUATION SUMMARY:
  Enterprise Value:  $      1,673,953M
  Equity Value:      $      1,673,953M
  Value per Share:   $         225.22

MARKET COMPARISON:
  Current Price:     $         480.84
  Upside/Downside:             -53.2%
  Assessment:        🔴 OVERVALUED

==================================================
```

## How It Works

### DCF Formula

**Enterprise Value = PV(Explicit FCF) + PV(Terminal Value)**

Where:

- **PV(Explicit FCF)** = Sum of discounted cash flows for forecast period
  - FCF<sub>t</sub> = FCF<sub>0</sub> × (1 + growth)<sup>t</sup>
  - PV = FCF<sub>t</sub> / (1 + WACC)<sup>t</sup>

- **Terminal Value** = Gordon Growth Model
  - TV = FCF<sub>final</sub> × (1 + terminal_growth) / (WACC - terminal_growth)
  - PV(TV) = TV / (1 + WACC)<sup>years</sup>

- **Value per Share** = Equity Value / Shares Outstanding

### Assessment Criteria

| Upside/Downside | Assessment | Signal |
|---|---|---|
| > +20% | **Undervalued** | 🟢 Buy signal |
| -20% to +20% | **Fairly Valued** | 🟡 Hold |
| < -20% | **Overvalued** | 🔴 Sell signal |

## Assumptions & Limitations

### Key Assumptions
1. **Debt-free company** - Equity value = Enterprise value (assumes no net debt)
2. **Free Cash Flow available** - Requires quarterly FCF in financial statements
3. **Stable WACC** - Discount rate assumed constant over forecast period
4. **Terminal growth <= GDP growth** - Terminal growth rate cannot exceed long-term economic growth
5. **Annualized quarterly FCF** - Quarterly FCF multiplied by 4 to get annual estimate

### Limitations
- **No debt adjustments** - Should adjust for net debt/cash in real analysis
- **No adjustments for tax** - Uses pre-tax FCF as provided by Yahoo Finance
- **Simple WACC calculation** - Uses beta and simplified risk premium (full WACC should include cost of debt)
- **Historical data only** - Cannot adjust for future capital structure changes
- **Market data delays** - Yahoo Finance data may lag by 15-20 minutes
- **Quarterly data only** - Some companies may have incomplete quarterly FCF data

## API Rate Limiting

The tool implements automatic rate limiting to respect Yahoo Finance API limits:
- **Limit**: 60 API calls per minute
- **Behavior**: Automatically delays requests if limit approaching
- **No API key required**: Uses free yfinance tier

## Roadmap & Future Enhancements

### v1.1.0 (In Progress)

#### ✨ CLI Arguments Support
- Non-interactive mode for batch analysis
- Custom parameter specification
- Ticker as command-line argument instead of prompt
- Example: `python app.py MSFT --growth 8 --wacc 10`

#### 📊 Scenario Analysis (Bull/Base/Bear)
- Run DCF with three market scenarios simultaneously
- Bull case: Optimistic growth and lower WACC
- Base case: Analyst consensus estimates
- Bear case: Conservative growth and higher WACC
- Compare valuations across scenarios
- Example: `python app.py MSFT --scenarios`

#### 📤 CSV Export
- Save valuation results to spreadsheet
- Includes year-by-year projections and summary metrics
- Useful for portfolio tracking and reporting
- Example: `python app.py MSFT --output results.csv`

#### 🔀 Multi-Stock Comparison
- Analyze 5+ stocks in single run
- Side-by-side valuation comparison
- Rank by upside/downside percentage
- Batch processing with results aggregation
- Example: `python app.py AAPL MSFT GOOGL TSLA --compare`

### v1.2.0 (Planned)

#### 📈 Sensitivity Analysis
- Show how valuation changes with input variations
- Sensitivity tables for key assumptions
- Identify most impactful variables
- Visualization of sensitivity ranges

#### 🛠️ Advanced Features
- **Unit Tests** - Full test coverage for calculations and data fetching
- **Logging System** - Comprehensive logging for debugging
- **Configuration File** - YAML/JSON for default parameters
- **Debt Adjustments** - Include net debt for enterprise-to-equity conversion
- **WACC Calculator** - More sophisticated cost of equity and debt calculation

## Common Issues

### "Invalid ticker or no data available"
- Check ticker spelling (must match Yahoo Finance symbols)
- Use only common US stocks/ETFs
- Some delisted stocks may not have data

### "No cash flow data available"
- Some companies or ETFs don't report quarterly FCF
- Try a different security
- Cash flow statements may be delayed for newly public companies

### "Free Cash Flow not in financial statements"
- Company may not have FCF reporting available
- Check if ticker is valid on Yahoo Finance website directly

### Rate limiting / Timeout errors
- Network connection issue
- Yahoo Finance servers may be temporarily unavailable
- Try again in a few seconds

## Financial Concepts

### Free Cash Flow (FCF)
Operating cash flow minus capital expenditures. Represents cash available to all investors.

### WACC (Weighted Average Cost of Capital)
Average rate of return required by all capital providers (equity and debt holders).

### Terminal Value
Estimated value of company beyond explicit forecast period, typically 60-80% of total value.

### Beta
Measure of stock volatility relative to market. > 1 = more volatile, < 1 = less volatile.

## Resources

- [Yahoo Finance API Documentation](https://finance.yahoo.com/)
- [DCF Valuation Methodology](https://www.investopedia.com/terms/d/dcf.asp)
- [WACC Explanation](https://www.investopedia.com/terms/w/wacc.asp)

## License

Open source - use and modify freely.
